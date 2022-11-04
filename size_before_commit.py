import sys
sys.path.append("./lib")
import Git
import os


import json
with open("./all_commits_by_date/" + "all_dates" + '.json', "r") as f:
    all_dates = json.load(f)

# dates = all_dates[4300:]

dates = all_dates

def iter_count(file_name):
    if not check_file(file_name):
        raise Exception("not a file")
    from itertools import (takewhile, repeat)
    buffer = 1024 * 1024
    with open(file_name, encoding="utf8", errors='ignore') as f:
        buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
        return sum(buf.count('\n') for buf in buf_gen)
    
def check_file(file_name):
    return os.path.exists(file_name)

def is_binary(file_path):
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    return is_binary_string(open(file_path, 'rb').read(1024))

def count_lns(files):
    c = 0

    for file_path in files:
        if not check_file(file_path):
            continue
        if is_binary(file_path):
            continue

        c += iter_count(file_path)
    return c


def collect(ins):
    dates, i, num_proc = ins
    length = len(dates) // num_proc
    if i == num_proc - 1:
        dates = dates[length * i :]
    else:
        dates = dates[length * i : length * (i+1)]

    repo_path = '/mnt/muhui/kernel_cve/L' + str(i)
    repo = Git.init(repo_path)
    repo_path += '/'

    month = dates[0][:7]
    for date in dates:
        try:
            if os.path.exists("./size_completed_log_" + str(i) + ".txt"):
                with open("./size_completed_log_" + str(i) + ".txt", "r") as f:
                    completed_dates = f.read()

                if date in completed_dates:
                    continue
            
            
            date_commit_lns_d = {}
            com_path = "./all_commits_by_date/" + date + "_info.json"
            with open(com_path, "r") as f:
                info = json.load(f)

            for commit_id in tqdm(info):    
                Git.reset(commit_id+"^")

                files = info[commit_id]['mod_files_lst']
                files = [repo_path + f for f in files]

                date_commit_lns_d[commit_id] = count_lns(files)
            
            
            with open("./size_info/" + date + '_info_size.json', "w") as f:
                json.dump(date_commit_lns_d, f, indent=1)
            #print(cur_date, '\n')
                
            with open("./size_completed_log_" + str(i) + ".txt", "a") as f:
                json.dump(date + "        ", f, indent=1)
        
        except Exception as e:
            with open("./size_err_log_" + str(i) + ".txt", "a") as f:
                json.dump(date + "  " + str(e) + "        ", f, indent=1)


if __name__ == '__main__':
    import multiprocessing as mp

    num_proc = 20
    pool = mp.Pool(num_proc)

    args = []
    for i in range(num_proc):
        args.append([dates, i, num_proc])
    pool.map(collect, args)
    pool.close()

