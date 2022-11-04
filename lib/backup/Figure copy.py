

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.pyplot import MultipleLocator
from matplotlib import rcParams
from matplotlib.ticker import FuncFormatter
import os
import json
# from matplotlib.backends.backend_pdf import PdfPages

NUM_TOTAL_COMMITS = 1122715
NUM_TOTAL_KVIC = 932

rcParams['font.family']='Times New Roman'

font1 = {
    'family' : 'Times New Roman',
#     'family' : 'Arial',
#     'family' : 'SimHei',
    'weight' : 'normal',
    'size'   : 36,
}

def load_hashes_of_date(date):
    with open("/Users/jinanjiang/Documents/LinuxCommits/all_commits_by_date/" + date + '.json', "r") as f:
        return json.load(f)
    
def load_info_of_date(date):
    with open("/Users/jinanjiang/Documents/LinuxCommits/all_commits_by_date/" + date + '_info.json', "r") as f:
        return json.load(f)

def get_all_dates():
    return load_hashes_of_date("all_dates")[:4064]

def get_all_info_keys():
    return ['num_adds_if', 'num_dels_if', 'num_mod_total_if', 'num_adds_loop', 'num_dels_loop', 'num_mod_total_loop', 'file_hash', 'num_adds', 'num_dels', 'num_mod_lns_total', 'num_mod_files', 'is_merge', 'parents', 'mod_files_lst', 'entropy', 'ppl_signed_off', 'ppl_acked', 'ppl_cc', 'ppl_reviewed', 'ppl_tested', 'ppl_reported', 'ppl_suggested', 'ppl_co_developed', 'fixes_lst', 'is_fix', 'mod_dirs', 'mod_sys', 'num_mod_dirs', 'num_mod_sys', 'author', 'author_email', 'committer', 'committer_email', 'author_date', 'committer_date']

def count_num_files_from(count_dict):
    def find_size(k):
        try:
            cur_path = "/Users/jinanjiang/Documents/LinuxCommits/linux/" + k
            cur_all_files = os.listdir(cur_path)
        except:
            return 1
        
        c = 0
        for f in cur_all_files:
            c += find_size(k + '/' + f)
        return c
    

    size_dict = {}
    for k in count_dict.keys():
        cur_path = "/Users/jinanjiang/Documents/LinuxCommits/linux/" + k

        if not os.path.exists(cur_path):
            size_dict[k] = None
        else:
            size_dict[k] = find_size(cur_path)
    return size_dict


def get_att_from_dates(dates, att, sub_folder = "", filter_merge = False, testing = False):
    # to get kvic info, use the subfolder old_kvic_cache or new_kvic_cache
    # for kvic, dates is a length-1 list, with only "old_kvic" or "new_kvic"
    
    # Note: for the organization of the cache, under fig_cache is for all dates,
    #       a subfolder under fig_cache is for specific categories of data (e.g. kvic, 2022-01).
    
    if sub_folder != "":
        sub_folder += "/"
    if filter_merge:
        sub_folder += "no_merge_"

    cache_path = "/Users/jinanjiang/Documents/LinuxCommits/fig_cache/" + sub_folder + att + ".json"
    
    if not testing:
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)
    l = []
    for date in dates:
        cur_date_info = load_info_of_date(date)

        for cur_hash in cur_date_info.keys():
            if filter_merge and cur_date_info[cur_hash]['is_merge']:
                continue
            if cur_hash in ['a101ad945113be3d7f283a181810d76897f0a0d6', \
                            'cd26f1bd6bf3c73cc5afe848677b430ab342a909']:
                continue
            l.append(cur_date_info[cur_hash][att])
    l.sort()
    
    if not testing:
        with open(cache_path, "w") as f:
            json.dump(l, f, indent=1)
    return l


def get_dir_sys_from_dates(dates, sub_folder = ""):
    # to get kvic info, use the subfolder old_kvic_cache or new_kvic_cache
    # for kvic, dates is a length-1 list, with only "old_kvic" or "new_kvic"
    from tqdm import tqdm
    
    att = "dir_sys_counts"
    if sub_folder != "":
        sub_folder += "/"

    cache_path = "./fig_cache/" + sub_folder + att + ".json"
    
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
        
    # find the total num from a given set of dates
    total_file = {}
    total_dir = {}
    total_sys = {}

    for date in tqdm(dates):
        cur_info = load_info_of_date(date)
        
        file_num_mod_dict, dir_num_mod_dict, sys_num_mod_dict = Git.get_num_mod_fl_dir_sys(cur_info)

        for k in file_num_mod_dict.keys():
            if k not in total_file.keys():
                total_file[k] = 0
            total_file[k] += file_num_mod_dict[k]

        for k in dir_num_mod_dict.keys():
            if k not in total_dir.keys():
                total_dir[k] = 0
            total_dir[k] += dir_num_mod_dict[k]

        for k in sys_num_mod_dict.keys():
            if k not in total_sys.keys():
                total_sys[k] = 0
            total_sys[k] += sys_num_mod_dict[k]
    
    sys_size_dict = count_num_files_from(total_sys)
    normalized_total_sys = {}
    for k in total_sys.keys():
        if sys_size_dict[k] is None:
            continue
        else:
            normalized_total_sys[k] = total_sys[k] / sys_size_dict[k]

    dir_size_dict = count_num_files_from(total_dir)
    normalized_total_dir = {}
    for k in total_dir.keys():
        if dir_size_dict[k] is None:
            continue
        else:
            normalized_total_dir[k] = total_dir[k] / dir_size_dict[k]
            
            
    result = {"file": total_file, "dir": normalized_total_dir, "sys": normalized_total_sys}
    with open(cache_path, "w") as f:
        json.dump(result, f, indent=1)
    return result

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


def get_cdf(kvic_in, non_kvic_in, normalize = False):
    import numpy as np
    
    # note: faster cdf: collect all data into a dictionary, sort it, and add up along the way
    max_coord = max(max(kvic_in), max(non_kvic_in))
    max_coord = int(max_coord) + 1
    
    gran = 10000
    length = max_coord / gran
    x = [i * length for i in range(gran)]
    y_kvic_count = [0] * gran
    y_non_kvic_count = [0] * gran
    
    for i in kvic_in:
        if i/length - i//length < 0.5:
            closer_ind = i//length
        else:
            closer_ind = i//length 
        y_kvic_count[int(closer_ind)] += 1
        
    for i in non_kvic_in:
        if i/length - i//length < 0.5:
            closer_ind = i//length
        else:
            closer_ind = i//length 
        y_non_kvic_count[int(closer_ind)] += 1
        
    y_kvic = np.cumsum(y_kvic_count)
    y_non_kvic = np.cumsum(y_non_kvic_count)
    
    if normalize:
        y_kvic = [i for i in y_kvic] 
        y_non_kvic = [i/len(non_kvic_in)*len(kvic_in) for i in y_non_kvic] 
    
    return x, y_kvic, y_non_kvic


def make_plot_cdf(x_kvic, x_non_kvic, y_non_kvic, y_kvic, title, left):
    # f = plt.figure()
    plt.rcParams['figure.figsize'] = (12.0, 8.0)  # 图像大小
    plt.rcParams['xtick.direction'] = 'in'  #x轴刻度向内
    plt.rcParams['ytick.direction'] = 'in'  #y轴刻度向内
    f = plt.figure()
    plt.xlabel(title,fontsize=37,labelpad=20)  # x轴
    plt.ylabel("CDF",fontsize=37,labelpad=20)  # y轴
    plt.semilogx(x_kvic,y_kvic,lw=5,marker='o',markersize=15,markevery=0.05,label='KVIC')  # KVIC 图像
    plt.semilogx(x_non_kvic,y_non_kvic,lw=5,marker='v',markersize=15,markevery=0.05,linestyle='--',label='Non-KVIC')  # 非 KVIC 图像
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
    
    plt.xlim(left=left)
    plt.show()
    # plt.savefig('01_Added_lines_of_each_commit.pdf')
    f.savefig(title + ".pdf", bbox_inches='tight')

def plot_attribute_cdf(non_kvic_commits, kvic_commits, attribute, title, left):
    
    # non_kvic_counts = [i[attribute] for i in non_kvic_commits.values()]
    # kvic_counts = [i[attribute] for i in kvic_commits.values()]
    
    non_kvic = non_kvic_commits
    kvic = kvic_commits
    
    # non_kvic = sorted(non_kvic_counts)
    # kvic = sorted(kvic_counts)

    x, y_kvic, y_non_kvic = get_cdf(kvic, non_kvic, normalize = True)
    
    print(y_kvic)
    
    make_plot_cdf(x, y_non_kvic, y_kvic, title, left)

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
    # y2 is used as KVIC
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
    b1 = ax1.bar(x_t, y1, width=width, color='#1f77b4', label='non-KVIC')
    b2 = ax1.bar([i+width for i in x_t], y2, width, color='#ff7f0e', label='KVIC')

    """
    # 绘制柱形图2---双Y轴
    ax2 = ax1.twinx()
    b2 = ax2.bar(x, y2, width=width, color='#ff7f0e', label='Number of commits')
    ax2.ticklabel_format(style='sci', scilimits=(-1,2), axis='y')
    ax2.yaxis.get_offset_text().set_fontsize(37)
    """

    # 坐标轴标签设置
    ax1.set_xlabel('dir name',fontsize=37)
    ax1.set_ylabel('Number of modifications',fontsize=37)
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