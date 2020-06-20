# -*- coding:utf-8 -*-

from pandas import DataFrame
from collections import defaultdict
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def plot_line_chart():
    x1 = [50, 100, 150, 200, 250, 300]
    metrics = ["BLEU(%)", "METEOR(%)"]
    markers = ["o", "s", "^", "x", "D"]
    embed = [[2.26, 2.13, 2.19, 2.12, 2.17, 2.02],
             [7.47, 7.15, 7.46, 7.39, 7.25, 7.28]]
    embedData = np.array(embed)
    for i in range(embedData.shape[0]):
        y = embedData[i, :]
        plt.plot(x1, y, label=metrics[i],
                 marker=markers[i], linewidth=1, markersize=7)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=12)
    plt.xlabel("Embedding Size", fontsize=14)
    plt.ylabel("BLEU/METEOR", fontsize=14)
    plt.xticks(x1)
    plt.ylim(0, 10)
    handles, labels = plt.gca().get_legend_handles_labels()
    order = [1, 2, 0]
    plt.legend(loc="center right", fontsize=14, ncol=1)
    plt.grid(True, linestyle="-.")
    plt.savefig("Embedding_Size.eps", format="eps")
    plt.show()


# def plot_histogram():
#     files = ['/Users/kingxu/result/ASE18result/nmt_bleu.txt',
#              '/Users/kingxu/result/ASE18result/nngen_bleu.txt',
#              '/Users/kingxu/result/ASE18result/cleaned_nmt_bleu.txt',
#              '/Users/kingxu/result/ASE18result/cleaned_nngen_bleu.txt',
#              '/Users/kingxu/result/ASE18result/nmt_meteor.txt',
#              '/Users/kingxu/result/ASE18result/nngen_meteor.txt',
#              '/Users/kingxu/result/ASE18result/cleaned_nmt_meteor.txt',
#              '/Users/kingxu/result/ASE18result/cleaned_nngen_meteor.txt']
#     lists = [txt2list(f) for f in files]
#     dicts = [list2dict(l) for l in lists]
#     bleu_dicts = dicts[:4]
#     meteor_dicts = dicts[4:]
#     bleu_data = np.zeros((10, 4), int)
#     meteor_data = np.zeros((10, 4), int)
#     for i, j in enumerate(bleu_dicts):
#         for a in range(10):
#             bleu_data[a, i] = j[a]
#     for i, j in enumerate(meteor_dicts):
#         for a in range(10):
#             meteor_data[a, i] = j[a]
#     print(bleu_data, meteor_data)
#     fig = plt.figure()
#     ax = fig.add_subplot()
#     ax.set_xlabel("METEOR Value", fontsize=14)
#     ax.set_ylabel("Count Number", fontsize=14)
#     ax.set_position([0.16, 0.26, 0.70, 0.62])
#     df = DataFrame(meteor_data,
#                    index=['[0.0,0.1)', '[0.1,0.2)', '[0.2,0.3)', '[0.3,0.4)',
#                           '[0.4,0.5)', '[0.5,0.6)', '[0.6,0.7)', '[0.7,0.8)',
#                           '[0.8,0.9)', '[0.9,1.0]'],
#                    columns=['origin/nmt', 'origin/nngen', 'cleaned/nmt', 'cleaned/nngen'])
#     df.columns.name = 'dataset/approach'
#     # plt.xlabel("BLEU value", fontsize=14)
#     # plt.ylabel("Number", fontsize=14)
#     df.plot(ax=ax, kind='bar')
#     plt.savefig("METEOR_dist.eps", format="eps")
#     plt.show()


def plot_histogram():
    files = ['/Users/kingxu/result/IJCAI19result/nmt_bleu.txt',
             '/Users/kingxu/result/IJCAI19result/nngen_bleu.txt',
             '/Users/kingxu/result/IJCAI19result/codisum_bleu.txt',
             '/Users/kingxu/result/IJCAI19result/nmt_meteor.txt',
             '/Users/kingxu/result/IJCAI19result/nngen_meteor.txt',
             '/Users/kingxu/result/IJCAI19result/codisum_meteor.txt']
    lists = [txt2list(f) for f in files]
    dicts = [list2dict(l) for l in lists]
    bleu_dicts = dicts[:3]
    meteor_dicts = dicts[3:]
    bleu_data = np.zeros((10, 3), int)
    meteor_data = np.zeros((10, 3), int)
    for i, j in enumerate(bleu_dicts):
        for a in range(10):
            bleu_data[a, i] = j[a]
    for i, j in enumerate(meteor_dicts):
        for a in range(10):
            meteor_data[a, i] = j[a]
    print(bleu_data, meteor_data)
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_xlabel("BLEU Value", fontsize=14)
    ax.set_ylabel("Count Number", fontsize=14)
    ax.set_position([0.16, 0.26, 0.70, 0.62])
    df = DataFrame(bleu_data,
                   index=['[0.0,0.1)', '[0.1,0.2)', '[0.2,0.3)', '[0.3,0.4)',
                          '[0.4,0.5)', '[0.5,0.6)', '[0.6,0.7)', '[0.7,0.8)',
                          '[0.8,0.9)', '[0.9,1.0]'],
                   columns=['nmt', 'nngen', 'codisum'])
    df.columns.name = 'approach'
    # plt.xlabel("BLEU value", fontsize=14)
    # plt.ylabel("Number", fontsize=14)
    df.plot(ax=ax, kind='bar')
    plt.savefig("BLEU_dist2.eps", format="eps")
    plt.show()


def txt2list(in_file):
    ret_list = []
    with open(in_file) as f:
        for num in f:
            ret_list.append(float(num))
    return ret_list


def list2dict(in_list):
    ret_dict = defaultdict(int)
    for i in in_list:
        cate = int(i * 10)
        cate = cate if cate != 10 else 9
        ret_dict[cate] += 1
    return ret_dict


def txt2dict(in_file):
    ret_dict = dict()
    with open(in_file) as f:
        for i, num in enumerate(f):
            ret_dict[i] = float(num)
    return ret_dict


def dict2set(in_dict, threshold):
    """
    Argments:
        in_dict {dict}
        threshold {str} -- "[0.1, 0.2]", "[0.1, 0.3)"
    """
    start = threshold[0]
    end = threshold[-1]
    vs = [float(i) for i in threshold[1:-1].split(',')]
    if start == '[':
        if end == ']':
            return set([i for i, j in in_dict.items() if vs[0] <= j <= vs[1]])
        else:
            return set([i for i, j in in_dict.items() if vs[0] <= j < vs[1]])
    else:
        if end == ']':
            return set([i for i, j in in_dict.items() if vs[0] < j <= vs[1]])
        else:
            return set([i for i, j in in_dict.items() if vs[0] < j < vs[1]])


# def plot_venn():
#     files = ['/Users/kingxu/result/ASE18result/nmt_bleu.txt',
#              '/Users/kingxu/result/ASE18result/nngen_bleu.txt',
#              '/Users/kingxu/result/ASE18result/cleaned_nmt_bleu.txt',
#              '/Users/kingxu/result/ASE18result/cleaned_nngen_bleu.txt',
#              '/Users/kingxu/result/ASE18result/nmt_meteor.txt',
#              '/Users/kingxu/result/ASE18result/nngen_meteor.txt',
#              '/Users/kingxu/result/ASE18result/cleaned_nmt_meteor.txt',
#              '/Users/kingxu/result/ASE18result/cleaned_nngen_meteor.txt']
#     dicts = [txt2dict(f) for f in files]
#     sets1 = [dict2set(d, "[0.0, 0.1)") for d in dicts]
#     sets2 = [dict2set(d, "[0.9, 1.0]") for d in dicts]
#     plt.figure()
#     subsets = sets2[:2]
#     venn2(subsets=subsets, set_labels=('NMT', 'NNGen'))
#     venn2_circles(subsets=subsets, linestyle='dotted', linewidth=1.0)
#     plt.savefig("BLEU1venn.eps", format="eps")
#     plt.show()


def plot_venn():
    files = ['/Users/kingxu/result/IJCAI19result/nmt_bleu.txt',
             '/Users/kingxu/result/IJCAI19result/nngen_bleu.txt',
             '/Users/kingxu/result/IJCAI19result/codisum_bleu.txt',
             '/Users/kingxu/result/IJCAI19result/nmt_meteor.txt',
             '/Users/kingxu/result/IJCAI19result/nngen_meteor.txt',
             '/Users/kingxu/result/IJCAI19result/codisum_meteor.txt']
    dicts = [txt2dict(f) for f in files]
    sets1 = [dict2set(d, "[0.0, 0.1)") for d in dicts]
    sets2 = [dict2set(d, "[0.9, 1.0]") for d in dicts]
    plt.figure()
    subsets = sets2[3:]
    venn3(subsets=subsets, set_labels=('NMT', 'NNGen', 'CoDiSum'))
    venn3_circles(subsets=subsets, linestyle='dotted', linewidth=1.0)
    plt.savefig("METEOR1venn2.eps", format="eps")
    plt.show()


def plot_box_chart():
    tips = sns.load_dataset('tips')
    sns.boxplot(x='day', y='total_bill', data=tips,
                linewidth=2,      # 线宽
                width=0.8,        # 箱之间的间隔比例
                fliersize=3,      # 异常点大小
                palette='hls',    # 设置调色板
                whis=1.5,         # 设置IQR
                notch=True,       # 设置是否以中值做凹槽
                order={'Thur', 'Fri', 'Sat', 'Sun'},  # 筛选类别
                )
    # 可以添加散点图
    sns.swarmplot(x='day', y='total_bill', data=tips, color='k',
                  size=3, alpha=0.8)
    plt.show()


def plot_violin_chart():
    tips = sns.load_dataset('tips')
    sns.violinplot(x='day', y='total_bill', data=tips,
                   linewidth=2,   # 线宽
                   width=0.8,     # 箱之间的间隔比例
                   palette='hls',  # 设置调色板
                   order={'Thur', 'Fri', 'Sat', 'Sun'},    # 筛选类别
                   scale='count',  # 测度小提琴图的宽度： area-面积相同,count-按照样本数量决定宽度,width-宽度一样
                   gridsize=50,   # 设置小提琴图的平滑度，越高越平滑
                   inner='box',   # 设置内部显示类型 --> 'box','quartile','point','stick',None
                   # bw = 0.8       # 控制拟合程度，一般可以不设置
                   )
    plt.show()


if __name__ == "__main__":
    # plot_line_chart()
    # plot_box_chart()
    plot_violin_chart()
