

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.pyplot import MultipleLocator
from matplotlib import rcParams
from matplotlib.ticker import FuncFormatter
# from matplotlib.backends.backend_pdf import PdfPages


rcParams['font.family']='Times New Roman'

font1 = {
    'family' : 'Times New Roman',
#     'family' : 'Arial',
#     'family' : 'SimHei',
    'weight' : 'normal',
    'size'   : 36,
}


def get_cdf(kvic_in, non_kvic_in, normalize = False):
    # note: faster cdf: collect all data into a dictionary, sort it, and add up along the way
    max_coord = max(max(kvic_in), max(non_kvic_in))
    max_coord = int(max_coord) + 1
    x = list(range(0, max_coord)) # equally slice the x range into 10000
    y_kvic = [0] * max_coord
    y_non_kvic = [0] * max_coord

    for i in range(len(kvic_in)):
        for j in range(len(x)):
            if kvic_in[i] <= x[j]:
                y_kvic[j] += 1


    for i in range(len(non_kvic_in)):
        for j in range(len(x)):
            if non_kvic_in[i] <= x[j]:
                y_non_kvic[j] += 1
    
    if normalize:
        y_kvic = [i/len(kvic_in) for i in y_kvic] 
        y_non_kvic = [i/len(non_kvic_in) for i in y_non_kvic] 
    return x, y_kvic, y_non_kvic

def make_plot_cdf(x, y_non_kvic, y_kvic, title):
    # f = plt.figure()
    plt.rcParams['figure.figsize'] = (12.0, 8.0)  # 图像大小
    plt.rcParams['xtick.direction'] = 'in'  #x轴刻度向内
    plt.rcParams['ytick.direction'] = 'in'  #y轴刻度向内
    f = plt.figure()
    plt.xlabel(title,fontsize=37,labelpad=20)  # x轴
    plt.ylabel("CDF",fontsize=37,labelpad=20)  # y轴
    plt.semilogx(x,y_kvic,lw=5,marker='o',markersize=15,markevery=0.05,label='KVIC')  # KVIC 图像
    plt.semilogx(x,y_non_kvic,lw=5,marker='v',markersize=15,markevery=0.05,linestyle='--',label='Non-KVIC')  # 非 KVIC 图像
    plt.xticks(fontsize=37)  # x轴刻度
    plt.yticks(fontsize=37)  # y轴刻度
    plt.legend(prop=font1)  # 图例
    ax=plt.gca()  #获得坐标轴的句柄
    ax.spines['bottom'].set_linewidth(3)  #设置底部坐标轴的粗细
    ax.spines['left'].set_linewidth(3)  #设置左边坐标轴的粗细
    ax.spines['right'].set_linewidth(3)  #设置右边坐标轴的粗细
    ax.spines['top'].set_linewidth(3)  #设置上部坐标轴的粗细
    ax.tick_params(which='both', width=3, pad=10)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=5)
    plt.show()
    # plt.savefig('01_Added_lines_of_each_commit.pdf')
    f.savefig(title + ".pdf", bbox_inches='tight')

def plot_attribute_cdf(non_kvic_commits, kvic_commits, attribute, title):
    non_kvic_counts = [i[attribute] for i in non_kvic_commits.values()]
    kvic_counts = [i[attribute] for i in kvic_commits.values()]

    non_kvic = sorted(non_kvic_counts)
    kvic = sorted(kvic_counts)

    x, y_kvic, y_non_kvic = get_cdf(kvic, non_kvic, normalize = True)
    make_plot_cdf(x, y_non_kvic, y_kvic, title)

def plot_column_single(x, y, title):
    # plot_column_double(x, y, "test")

    f = plt.figure()
    plt.rcParams['figure.figsize'] = (12.0, 8.0)
    plt.rcParams['xtick.direction'] = 'in'  #x轴刻度向内
    plt.rcParams['ytick.direction'] = 'in'  #y轴刻度向内
    # plt.title('top 5 files')
    plt.xlabel("Subsystem name",fontsize=37)  # x轴
    plt.ylabel("Modified times",fontsize=37)  # y轴
    # plt.xticks(fontsize=37, rotation=300)
    plt.xticks(fontsize=37)
    plt.yticks(fontsize=37)
    ax=plt.gca()  #获得坐标轴的句柄
    ax.spines['bottom'].set_linewidth(3)  #设置底部坐标轴的粗细
    ax.spines['left'].set_linewidth(3)  #设置左边坐标轴的粗细
    ax.spines['right'].set_linewidth(3)  #设置右边坐标轴的粗细
    ax.spines['top'].set_linewidth(3)  #设置上部坐标轴的粗细
    ax.tick_params(which='both', width=3)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=5)
    
    y_max = max(y) * 1.2
    plt.ylim(0,y_max)  # y轴范围
    # plt.barh(x, y)
    plt.bar(x, y)
    for a, b in zip(x, y):
        ax.text(a, b+0.1, b, ha='center', va='bottom', fontsize=37)
    plt.show()
    f.savefig(title, bbox_inches='tight')


def plot_column_double(x, y1, y2, title):
    f = plt.figure()
    fig, ax1 = plt.subplots()

    plt.rcParams['figure.figsize'] = (12.0, 8.0)
    plt.yticks(fontsize=37)
    plt.xticks(fontsize=37, rotation=330)

    max_y = max(max(y1), max(y2)) * 1.2
    plt.ylim(0,max_y)

    ax=plt.gca()  #获得坐标轴的句柄
    ax.spines['bottom'].set_linewidth(3)  #设置底部坐标轴的粗细
    ax.spines['left'].set_linewidth(3)  #设置左边坐标轴的粗细
    ax.spines['right'].set_linewidth(3)  #设置右边坐标轴的粗细
    ax.spines['top'].set_linewidth(3)  #设置上部坐标轴的粗细
    ax.tick_params(which='both', width=3)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=5)

    # 柱形的宽度
    width = 0.4

    # 绘制柱形图1
    x_t = list(range(len(x)))
    b1 = ax1.bar(x_t, y1, width=width, color='#1f77b4', label='Number of CVEs')
    b2 = ax1.bar([i+width for i in x_t], y2, width, color='#ff7f0e', label='Number of 242432')

    """
    # 绘制柱形图2---双Y轴
    ax2 = ax1.twinx()
    b2 = ax2.bar(x, y2, width=width, color='#ff7f0e', label='Number of commits')
    ax2.ticklabel_format(style='sci', scilimits=(-1,2), axis='y')
    ax2.yaxis.get_offset_text().set_fontsize(37)
    """

    # 坐标轴标签设置
    ax1.set_xlabel('Year',fontsize=37)
    ax1.set_ylabel('Number of CVEs',fontsize=37)
    """
    ax2.set_ylabel('Number of commits',fontsize=37)
    """

    # x轴标签旋转
    # ax1.set_xticklabels(ax1.get_xticklabels(),rotation = 330)

    # # 双Y轴标签颜色设置
    # ax1.yaxis.label.set_color(b1[0].get_facecolor())
    # ax2.yaxis.label.set_color(b2[0].get_facecolor())

    # # 双Y轴刻度颜色设置
    # ax1.tick_params(axis = 'y', colors = b1[0].get_facecolor())
    # ax2.tick_params(axis = 'y', colors = b2[0].get_facecolor())

    # 图例设置
    plt.legend(handles = [b1, b2], prop=font1, loc = 2)

    #plt.xticks(x, year)
    plt.yticks(fontsize=37)

    #plt.ylim(0,140000)

    ax=plt.gca()  #获得坐标轴的句柄
    ax.spines['bottom'].set_linewidth(3)  #设置底部坐标轴的粗细
    ax.spines['left'].set_linewidth(3)  #设置左边坐标轴的粗细
    ax.spines['right'].set_linewidth(3)  #设置右边坐标轴的粗细
    ax.spines['top'].set_linewidth(3)  #设置上部坐标轴的粗细
    ax.tick_params(which='both', width=3)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=5)

    plt.show()
    fig.savefig(title, bbox_inches='tight')