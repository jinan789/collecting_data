import sys
sys.path.append("./lib")
import Git

repo_path = "/Users/jinanjiang/Documents/LinuxCommits/linux"
# repo_path = "/home/jiangjinan/linux"
repo = Git.init(repo_path)

import json
with open("./all_commits_by_date/" + "all_dates" + '.json', "r") as f:
    all_dates = json.load(f)
   
dates = all_dates

for date in dates:
    try:
        with open("./all_commits_by_date/" + date + '.json', "r") as f:
            cur_date = json.load(f)

        infos = Git.get_info_from_commits(cur_date)
        with open("./all_commits_by_date/" + date + '_info.json', "w") as f:
            json.dump(infos, f, indent=1)
            
        with open("completed_log.txt", "a") as f:
            json.dump(date + "        ", f, indent=1)
    except:
        with open("err_log.txt/", "a") as f:
            json.dump(date + "        ", f, indent=1)