import os
import git
import json
import sys
sys.path.append("./lib")
import Git
from tqdm import tqdm
import re
from Figure import *
import random

repo_path = "/home/jinan/linux"
repo = Git.init(repo_path)

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


all_dates = get_all_dates()


all_dates_lst = []
for date in all_dates:
    com_path = "./all_commits_by_date/" + date + ".json"
    with open(com_path, "r") as f:
        coms = json.load(f)
        for com in coms:
            all_dates_lst.append((date, com))

all_dates_lst = sorted(all_dates_lst, key = lambda x:x[0])
all_dates_lst = list(reversed(all_dates_lst))

Ns = [1000, 2000, 3000, 4000, 5000, 10000, 30000, 50000]

for N in Ns:
    print(N)
    if os.path.exists("./rand_res/" + str(N) + '.json'):
        continue




    commit_lst = []

    com_lst_path = "./rand_res/" + str(N) + '_rand_com_list.json'
    if os.path.exists(com_lst_path):
        with open(com_lst_path, "r") as f:
            commit_lst = json.load(f)
    else:
        print(1111)

        temp_set = set()
        while len(temp_set) != N:
            temp_set.add(random.choice(all_dates_lst))
        commit_lst = list(temp_set)
        commit_lst = sorted(commit_lst, key = lambda x:x[0])
        commit_lst = list(reversed(commit_lst))
        with open(com_lst_path, "w") as f:
            json.dump(commit_lst, f, indent=1)

    commit_lst = sorted(commit_lst, key = lambda x:x[0])
    commit_lst = list(reversed(commit_lst))


    

    repo_path = "/home/jinan/linux/"

    size_d = {}
    
    if os.path.exists("./rand_res/dict_cache_" + str(N) + ".json"):
        
        with open("./rand_res/dict_cache_" + str(N) + ".json", "r") as f:
            dict_cache = json.load(f)
            temp = {}
            for k in dict_cache:
                this_date, this_commit = k.split('**')
                temp[(this_date, this_commit)] = dict_cache[k]
            dict_cache = temp
    else:
        dict_cache = {}
   
    size_d = dict_cache
    count = 0
    for t in tqdm(commit_lst):
        t = tuple(t)
        if t in size_d:
            size_d[t] = dict_cache[t]
            count += 1
            continue
        date, commit_id = t
        com_path = "./all_commits_by_date/" + date + "_info.json"
        with open(com_path, "r") as f:
            info = json.load(f)
        Git.reset(commit_id+"^")

        files = info[commit_id]['mod_files_lst']
        files = [repo_path + f for f in files]

        t = tuple(t)
        size_d[t] = count_lns(files)
        
        if count % 30 == 0:
            new_size_d = {}
            for k in size_d:
                new_size_d[k[0] + '**' + k[1]] = size_d[k]

            with open("./rand_res/dict_cache_" + str(N) + ".json", "w") as f:
                json.dump(new_size_d, f, indent=1)

        count += 1


    new_size_d = {}

    for k in size_d:
        new_size_d[k[0] + '**' + k[1]] = size_d[k]
    with open("./rand_res/" + str(len(commit_lst)) + '.json', "w") as f:
        json.dump(new_size_d, f, indent=1)
