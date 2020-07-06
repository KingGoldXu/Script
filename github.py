import os
import subprocess
import json
import numpy as np
import matplotlib.pyplot as plt
import chardet


def rename_repo(dir):
    files = os.listdir(dir)
    dirs = [file for file in files if os.path.isdir(os.path.join(dir, file))]
    for sub_dir in dirs:
        os.chdir(os.path.join(dir, sub_dir))
        p = subprocess.Popen(['git', 'remote', '-v'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        stdout = p.stdout.read().decode('utf-8', 'ignore')
        str_list = stdout.split()
        repo = None
        if len(str_list) > 2:
            url = str_list[1]
            if url.startswith('https://github.com/'):
                repo = url[19:-4]
                repo = repo.replace('/', '_')
            elif url.startswith('git://github.com/'):
                repo = url[17:-4]
                repo = repo.replace('/', '_')
        files_updated = os.listdir(dir)
        dirs_updated = [file for file in files if os.path.isdir(
            os.path.join(dir, file))]
        if repo and repo not in dirs_updated:
            print("Rename {} to {}".format(sub_dir, repo))
            os.rename(os.path.join(dir, sub_dir), os.path.join(dir, repo))
        else:
            print("Can't rename " + sub_dir)


def update_repo(dir):
    files = os.listdir(dir)
    dirs = [file for file in files if os.path.isdir(os.path.join(dir, file))]
    for sub_dir in dirs:
        os.chdir(os.path.join(dir, sub_dir))
        p = subprocess.Popen(['git', 'pull'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print("Update {}".format(sub_dir))
        print("stdout----------------")
        print(stdout.decode('utf-8', 'ignore'))
        print("stderr----------------")
        print(stderr.decode('utf-8', 'ignore'))
        print("----------------------")


def extract_atomic_change(dir):
    files = os.listdir(dir)
    dirs = [file for file in files if os.path.isdir(os.path.join(dir, file))]
    for sub_dir in dirs:
        p = subprocess.Popen(['java', '-Xss128M', '-jar', 'mdiff_2.0.jar', '-ace',
                              '-r', os.path.join(dir, sub_dir),
                              '-o', '/mnt/data1/kingxu/atomic_changes/{}.json'.format(sub_dir)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print("Process {}".format(sub_dir))
        print("stdout----------------")
        print(stdout.decode('utf-8', 'ignore'))
        print("stderr----------------")
        print(stderr.decode('utf-8', 'ignore'))
        print("----------------------")


def json_to_dot(json_str, filename):
    ast = json.loads(json_str)
    nn = NodeName()
    dot = DotFile('digraph {')
    root = list(ast.items())
    if len(root) != 1:
        return None
    output_dot(root[0], None, dot, nn)
    dot.append('\n}')
    print(dot.dot_str)
    dot.write(filename)


def output_dot(root, parent_name, dot, nn):
    parent, child = root
    nd_name = nn.next_node_name()
    dot.append('\n' + nd_name +
               ' [label=' + json.dumps(parent, ensure_ascii=False) + '];')
    if parent_name is not None:
        dot.append('\n' + parent_name + ' -> ' + nd_name + ';')
    if isinstance(child, str):
        child_name = nn.next_node_name()
        dot.append('\n' + child_name +
                   ' [label=' + json.dumps(child, ensure_ascii=False) + '];')
        dot.append('\n' + nd_name + ' -> ' + child_name + ';')
    elif isinstance(child, dict):
        for child in child.items():
            output_dot(child, nd_name, dot, nn)
    elif isinstance(child, list):
        for i in child:
            if isinstance(i, str):
                child_name = nn.next_node_name()
                dot.append('\n' + child_name +
                           ' [label=' + json.dumps(i, ensure_ascii=False) + '];')
                dot.append('\n' + nd_name + ' -> ' + child_name + ';')
            elif isinstance(i, dict):
                for ii in i.items():
                    output_dot(ii, nd_name, dot, nn)


class NodeName():
    def __init__(self):
        self.nodeCount = 0

    def next_node_name(self):
        self.nodeCount += 1
        return "n{}".format(self.nodeCount)


class DotFile():
    def __init__(self, str):
        self.dot_str = str

    def append(self, str):
        self.dot_str += str

    def write(self, filename):
        with open(filename, 'w') as f:
            f.write(self.dot_str)


def ast_state(json_file):
    atomic_changes = json.load(open(json_file, 'r'))
    state = []
    pruned_state = []
    for i in atomic_changes:
        state.append(i['old_stat'])
        state.append(i['new_stat'])
        pruned_state.append(i['old_psta'])
        pruned_state.append(i['new_psta'])
    leaf_node_state = []
    not_leaf_node_state = []
    max_depth_state = []
    pruned_leaf_node_state = []
    pruned_not_leaf_node_state = []
    pruned_max_depth_state = []
    for i in state:
        states = i.split()
        leaf_node_state.append(int(states[0]))
        not_leaf_node_state.append(int(states[1]))
        max_depth_state.append(int(states[2]))
    for i in pruned_state:
        states = i.split()
        pruned_leaf_node_state.append(int(states[0]))
        pruned_not_leaf_node_state.append(int(states[1]))
        pruned_max_depth_state.append(int(states[2]))
    arrays = [np.array(leaf_node_state), np.array(pruned_leaf_node_state),
              np.array(not_leaf_node_state), np.array(
                  pruned_not_leaf_node_state),
              np.array(max_depth_state), np.array(pruned_max_depth_state)]
    fig = plt.figure(figsize=(8, 6))
    plt.boxplot(arrays, notch=False, sym='o', vert=True)
    plt.xticks([x+1 for x in range(len(arrays))],
               ['leaf', 'pruned_leaf', 'not_leaf', 'pruned_not_leaf', 'depth', 'pruned_depth'])
    title = json_file.split('/')[-1][:-5]
    plt.title(title + '({})'.format(len(state)))
    plt.show()


def wrap_ast_state(dir):
    files = os.listdir(dir)
    for f in files:
        file = os.path.join(dir, f)
        ast_state(file)


def random_gen_pic(json_file):
    atomic_changes = json.load(open(json_file, 'r'))
    first_ten = atomic_changes[:10]
    for i in first_ten:
        old_pruned_ast = i['old_past']
        new_pruned_ast = i['new_past']
        old_dot_file = '/Users/kingxu/tmp/dot/{}_{}.dot'.format(i['id'], 'old')
        new_dot_file = '/Users/kingxu/tmp/dot/{}_{}.dot'.format(i['id'], 'new')
        json_to_dot(old_pruned_ast, old_dot_file)
        json_to_dot(new_pruned_ast, new_dot_file)
        old_pdf_file = '/Users/kingxu/tmp/pdf1/{}_{}.pdf'.format(i['id'], 'old')
        new_pdf_file = '/Users/kingxu/tmp/pdf1/{}_{}.pdf'.format(i['id'], 'new')
        p = subprocess.Popen(['dot', '-Tpdf', old_dot_file, '-o', old_pdf_file],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print(stderr)
        p = subprocess.Popen(['dot', '-Tpdf', new_dot_file, '-o', new_pdf_file],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print(stderr)


def merge_atomic_change(dir):
    files = os.listdir(dir)
    json_files = [file for file in files if file.endswith(".json")]
    atomic_changes = []
    content_set = set()
    for file in json_files:
        full_path = os.path.join(dir, file)
        changes = json.load(open(full_path))
        # content_set = set()
        for change in changes:
            # filter out no-ascii message
            if chardet.detect(str.encode(change['message']))['encoding'] != 'ascii':
                continue
            # filter out small message
            if len(change['message'].split(' ')) < 4:
                continue
            # filter out duplicate change
            content = change['message'] + change['old_code'] + change['new_code']
            if content in content_set:
                continue
            # TODO: filter out big ast

            content_set.add(content)
            atomic_changes.append(change)
    print(f'total {len(atomic_changes)} atomic changes!')
    with open('atomic_changes.json', 'w') as f:
        f.write(json.dumps(atomic_changes, indent=4))


if __name__ == "__main__":
    # rename_repo('/mnt/data1/source_code/')
    # update_repo('/mnt/data1/source_code/')
    # extract_atomic_change('/mnt/data1/source_code')
    # json_to_dot(open('/Users/kingxu/tmp/ast.json').read(), '/Users/kingxu/tmp/method_textblock.dot')
    # ast_state('/Users/kingxu/tmp/atomic_change/hibernate_hibernate-ogm.json')
    # wrap_ast_state('/Users/kingxu/tmp/atomic_change')
    # random_gen_pic('/Users/kingxu/tmp/okhttp_atomic_changes.json')
    merge_atomic_change('/mnt/data1/kingxu/atomic_changes')
