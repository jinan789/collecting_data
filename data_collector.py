import sys
sys.path.append("./lib")
import Git
import os

repo_path = "/Users/jinanjiang/Documents/LinuxCommits/linux"
repo_path = "/home/jiangjinan/linux"
repo = Git.init(repo_path)

import json
with open("./all_commits_by_date/" + "all_dates" + '.json', "r") as f:
    all_dates = json.load(f)
   

dates = all_dates[:4300]

def collect(ins):
    dates, i, num_proc = ins
    length = len(dates) // num_proc
    if i == num_proc - 1:
        dates = dates[length * i :]
    else:
        dates = dates[length * i : length * (i+1)]

    month = dates[0][:7]
    for date in dates:
        cur_month = date[:7]
        """
        if cur_month != month:
            month = cur_month
            os.system("git add *")
            os.system("git commit -m \"1\"")
            os.system("git push")
        """

        try:
            with open("./completed_log_" + str(i) + ".txt", "r") as f:
                completed_dates = json.load(f)

            if date in completed_dates:
                continue
            
            with open("./all_commits_by_date/" + date + '.json', "r") as f:
                cur_date = json.load(f)

            infos = Git.get_info_from_commits(cur_date)
            with open("./all_commits_by_date/" + date + '_info.json', "w") as f:
                json.dump(infos, f, indent=1)
            #print(cur_date, '\n')
                
            with open("./completed_log_" + str(i) + ".txt", "a") as f:
                json.dump(date + "        ", f, indent=1)
        except Exception as e:
            with open("./err_log_" + str(i) + ".txt", "a") as f:
                json.dump(date + "  " + str(e) "        ", f, indent=1)


if __name__ == '__main__':
    import multiprocessing as mp

    num_proc = 20
    pool = mp.Pool(num_proc)

    args = []
    for i in range(num_proc):
        args.append([dates, i, num_proc])
    pool.map(collect, args)
    pool.close()

