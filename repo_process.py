# -*- encoding: utf-8 -*-

import os
import sys
import subprocess
import json
import re
import time
from pygments import highlight
from pygments.lexers import JavaLexer
from pygments.formatters import RawTokenFormatter


def get_file_contents_by_hash(hash_code):
    """ 根据提供的hash短码使用'git cat-file -p'命令从repo中获取完整文件.

    Arguments:
        hash_code {str} -- hash短码

    Returns:
        str -- 包含整个文件的字符串
    """
    # cmd = 'git cat-file -p ' + hash_code
    # child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    child = subprocess.Popen(['git', 'cat-file', '-p', hash_code],
                             stdout=subprocess.PIPE)
    ret = child.stdout.read().decode('utf-8', 'ignore')
    child.wait()
    return ret


def get_commits_in_repo(repo_dir='./'):
    """ 根据提供的repo的路径,提取出所有涉及到java文件变动的commits,
        每个commit只提取了java文件名和对应的hash短码,
        具体是读取'git log -p'命令的输出并提取必要信息.

    Arguments:
        repo_dir {str} -- 项目的目录

    Returns:
        list -- 由commit组成的list.
    """
    if not os.path.exists(repo_dir):
        return None
    os.chdir(repo_dir)
    child1 = subprocess.Popen(['git', 'log', '-p', '--no-merges'],
                              stdout=subprocess.PIPE)
    header_start = False
    commits = []
    commit = {}
    files = []
    hash_code = ''
    message = ''
    file_pair = {}
    file1, file2 = '', ''
    line = child1.stdout.readline().decode('utf-8', 'ignore')
    while line:
        if line.startswith('commit'):
            # new commit, save the old one
            if file1 and file2:
                file_pair['file1'] = file1
                file_pair['file2'] = file2
                files.append(file_pair)
            if message and files and hash_code:
                commit['hash'] = hash_code
                commit['message'] = message.strip('\r\n')
                commit['files'] = files
            # changed more than 10 files, filter out, run faster
            if commit and len(files) <= 10:
                commits.append(commit)
            file1, file2 = '', ''
            file_pair = {}
            message = ''
            files = []
            commit = {}
            header_start = True
            hash_code = line[7: -1]
        if header_start and line[0] in ' \r\n\t':
            message += line
        if line.startswith('diff --git'):
            # new files, save the old ones
            if file1 and file2:
                file_pair['file1'] = file1
                file_pair['file2'] = file2
                files.append(file_pair)
            file1, file2 = '', ''
            file_pair = {}
            header_start = False
            lt = line[:-1].split(' ')
            if len(lt) == 4 and lt[-2].endswith('.java') and \
                    lt[-1].endswith('.java'):
                file1 = lt[-2][2:]
                file2 = lt[-1][2:]
        if line.startswith('index') and file1 and file2:
            index = line.split(' ')[1]
            indexs = index.split('..')
            if len(indexs) == 2:
                file1 = file1 + '\t' + indexs[0].strip(' \r\n\t')
                file2 = file2 + '\t' + indexs[1].strip(' \r\n\t')
        line = child1.stdout.readline().decode('utf-8', 'ignore')
    repo = repo_dir.strip('/').split('/')[-1]
    json.dump(commits, open("/mnt/data1/kingxu/{}.commits.json".format(repo),
                            'w'))
    return commits


def extract_files(json_file, repo_base, base_path):
    """ 为某个项目的commits提取所有对应的java文件,文件存放在对应文件夹中,
        文件名为短hash值,因为一个项目中的hash值是唯一的.

    Arguments:
        json_file {string} -- 文件名,以'.commits.json'结尾
        repo_base {string} -- repo所在的文件夹,不需要指定repo,从json_file获得
        base_path {string} -- 指定的存java文件的文件夹所在的路径
    """
    commits = json.load(open(json_file, 'r'), encoding='utf-8')
    json_file = json_file.split('/')[-1]
    dir_name = json_file[:-13]
    repo_dir = os.path.join(repo_base, dir_name)
    dir = os.path.join(base_path, dir_name)
    hash_set = set()
    if not os.path.exists(dir):
        os.mkdir(dir)
    for commit in commits:
        for file_pair in commit['files']:
            file1, file2 = file_pair['file1'], file_pair['file2']
            l1, l2 = file1.split('\t'), file2.split('\t')
            if len(l1) == 2 and len(l2) == 2:
                hash_set.add(l1[1])
                hash_set.add(l2[1])
    os.chdir(repo_dir)
    for i in list(hash_set):
        f_content = get_file_contents_by_hash(i)
        if f_content:
            f_name = os.path.join(dir, '{}.java'.format(i))
            with open(f_name, 'w') as f:
                f.write(f_content)


def extract_class_and_method(java_dir, base_path):
    """ 为每个java文件提取class,function,attribute,name.
        以文件的hash为key,存为json文件
    """
    if not os.path.isdir(java_dir):
        return None
    files = os.listdir(java_dir)
    names_dict = {}
    for f in files:
        h, i = os.path.splitext(f)
        if i == '.java':
            classnames = set()
            methodnames = set()
            attributenames = set()
            names = set()
            with open(os.path.join(java_dir, f)) as fl:
                cont = fl.read()
                x = highlight(cont, JavaLexer(), RawTokenFormatter())
                for y in str(x, encoding='utf-8').splitlines():
                    ys = y.split('\t')
                    if ys[0] == 'Token.Name.Class':
                        classnames.add(eval(ys[1]))
                    elif ys[0] == 'Token.Name.Function':
                        methodnames.add(eval(ys[1]))
                    elif ys[0] == 'Token.Name.Attribute':
                        attributenames.add(eval(ys[1]))
                    elif ys[0] == 'Token.Name':
                        names.add(eval(ys[1]))
            names_dict[h] = {'NC': list(classnames),
                             'NF': list(methodnames),
                             'NA': list(attributenames),
                             'N': list(names)}
    repo = java_dir.strip('/').split('/')[-1]
    jf = os.path.join(base_path, '{}.names.json'.format(repo))
    json.dump(names_dict, open(jf, 'w'))
    return names_dict


def write_files_in_directory(commits, base_path):
    """ 将commits中的每组文件对提取到base_path指定的文件夹中,
        给文件对赋一个index,并以index为文件名存储两个文件

    Arguments:
        commits {list} -- 由get_commits_in_repo函数返回的列表
        base_path {string} -- 以string指定的文件路径
    """
    index = 1
    for commit in commits:
        for file_pair in commit['files']:
            file1, file2 = file_pair['file1'], file_pair['file2']
            l1, l2 = file1.split('\t'), file2.split('\t')
            if len(l1) == 2 and len(l2) == 2:
                f1_content = get_file_contents_by_hash(l1[1])
                f2_content = get_file_contents_by_hash(l2[1])
                if f1_content and f2_content:
                    file_pair['index'] = index
                    dir = os.path.join(base_path, str(index))
                    if not os.path.exists(dir):
                        os.mkdir(dir)
                    file1_name = os.path.join(dir, 'old.java')
                    file2_name = os.path.join(dir, 'new.java')
                    with open(file1_name, 'w') as f1:
                        f1.write(f1_content)
                    with open(file2_name, 'w') as f2:
                        f2.write(f2_content)
                    index += 1
    json_file = os.path.join(base_path, 'commits1.json')
    with open(json_file, 'w') as f:
        json.dump(commits, f)


def is_message_contain_code(commit):
    """ 给定一个commit,判断commit message中是否包括了代码片段的commit.
        代码片段包括class name,method name,variable name等.
        准备采用get_file_contents_by_hash提取变动的java文件的内容,
        使用pygments从java文件中获取name.

    Arguments:
        commit {dict} -- commits中的元素

    Returns:
        bool -- True如果包含
    """

    names, words = set(), set()
    for file_pair in commit['files']:
        file1, file2 = file_pair['file1'], file_pair['file2']
        l1, l2 = file1.split('\t'), file2.split('\t')
        if len(l1) == 2 and len(l2) == 2:
            f1_content = get_file_contents_by_hash(l1[1])
            f2_content = get_file_contents_by_hash(l2[1])
            for f_content in [f1_content, f2_content]:
                x = highlight(f_content, JavaLexer(), RawTokenFormatter())
                for y in str(x, encoding='utf-8').splitlines():
                    ys = y.split('\t')
                    if ys[0].startswith('Token.Name') and \
                            ys[0] != 'Token.Name.Decorator':
                        names.add(eval(ys[1]))
    message = commit['message'].splitlines()[0]
    pattern = re.compile(r'[_a-zA-Z][_a-zA-Z0-9]*')
    words = set(pattern.findall(message))
    return words.intersection(names)


def commit_with_class_method(base_path, repo):
    """ 为每个commit提供可能和代码中的元素重合的候选
    """
    cs_name = '{}.commits.json'.format(repo)
    ns_name = '{}.names.json'.format(repo)
    commits = json.load(open(os.path.join(base_path, cs_name)))
    names = json.load(open(os.path.join(base_path, ns_name)))
    pattern = re.compile(r'[_a-zA-Z][_a-zA-Z0-9]*')
    for c in commits:
        cn, fn, an, n = [], [], [], []
        token = []
        m_line = c['message'].splitlines()
        for i in m_line:
            if not i.strip(' \t\r\n'):
                break
            token += pattern.findall(i)
        for file_pair in c['files']:
            file1, file2 = file_pair['file1'], file_pair['file2']
            l1, l2 = file1.split('\t'), file2.split('\t')
            if len(l1) == 2 and len(l2) == 2:
                for h in [l1[1], l2[1]]:
                    if h in names:
                        cn += names[h]['NC']
                        fn += names[h]['NF']
                        an += names[h]['NA']
                        n += names[h]['N']
        cn, fn, an, n = set(cn), set(fn), set(an), set(n)
        token = set(token)
        tcn = list(token.intersection(cn))
        tfn = list(token.intersection(fn))
        tan = list(token.intersection(an))
        tn = list(token.intersection(n))
        c['append'] = {'NC': tcn, 'NF': tfn, 'NA': tan, 'N': tn}
    json.dump(commits, open(os.path.join(base_path, cs_name), 'w'))


def parse_java_to_AST(tool_path, java_dir):
    """ 使用提供的工具处理base_path文件夹中的所有java文件并生成AST保存

    Argments:
        tool_path {string} -- 指定工具文件
        java_dir {string} -- 指定需要处理的文件夹
    """

    if not os.path.isdir(java_dir):
        return None
    files = os.listdir(java_dir)
    for f in files:
        h, i = os.path.splitext(f)
        if i == '.java':
            cmd = [tool_path, 'parse', os.path.join(java_dir, f)]
            child = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            ret = child.stdout.read().decode('utf-8', 'ignore')
            child.wait()
            with open(os.path.join(java_dir, '{}.ast'.format(h)),
                      'w') as fo:
                fo.write(ret)
