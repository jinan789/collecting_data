import git
import sys
import math
import json

"""
import sys
sys.path.append("./lib")
from Git import *
"""

def init(repo_path):
    global git
    repo = git.Repo(repo_path)
    git = repo.git
    return repo

def reset(commit):
    git.reset("--hard", commit)
    
def get_commit(commit):
    return git.log(commit, "-1").split("\n")[0].split()[1]

def get_HEAD():
    return get_commit("HEAD")

def get_all_commits_from(repo, commit = None, max_count = None):
    if commit is None:
        commit = get_HEAD()
    if max_count is None:
        all_commits = list(repo.iter_commits(commit))
    else:
        all_commits = list(repo.iter_commits(commit, max_count = max_count))
    all_commits_hash = [c.hexsha for c in all_commits]
    
    return all_commits_hash



def get_modified_lines(commit, filter_empty_line = 1, filter_comments = False):
    # returns dict
    #    key: filename
    #    value: list of modified lines for this file

    diff_text = git.diff(commit+"^!", "-z").split('\n')
    diff_text = [i for i in diff_text if i.startswith("diff") or i.startswith("+") or i.startswith("-")]
    
    if filter_empty_line:
        diff_text = [i for i in diff_text if (i != "+" and i != "-")]
        
    if filter_comments:
        in_comment = False
        res = []
        try:
            for i in diff_text:
                cur_line = i[1:].strip()
                if in_comment:
                    if '*/' in cur_line:
                        in_comment = False
                        if cur_line.endswith('*/'):
                            continue
                        else:
                            res.append(i)
                            continue
                if cur_line.startswith('/*'):
                    if '*/' in cur_line:
                        continue
                    in_comment = True
                    continue
                if cur_line.startswith('//'):
                    continue
                res.append(i)
            diff_text = res
        except Exception as e:
            with open("get_com.txt", 'a') as f:
                json.dump('**********' + str(e) + "       " + commit + '**********', f, indent=1)

    file_to_mod_lines_dict = {}
    file_nm = None
    
    cur_line = 0
    num_total_lines = len(diff_text)
    while cur_line < num_total_lines:
        cur_text = diff_text[cur_line]
        if cur_text[:4] == 'diff':
            file_nm = cur_text.split()[-1]

            if file_nm[:2] == "a/":
                raise Exception("wrong wrong wrong")
            if file_nm[:2] == "b/":
                file_nm = file_nm[2:]

            
            file_to_mod_lines_dict[file_nm] = []

            if cur_line + 1 == num_total_lines:
                # no more lines to consume, just exit
                break
            next_line_st = diff_text[cur_line + 1][0]
            if next_line_st == "+" or next_line_st == "-":
                cur_line += 3 # skip 2 lines
            else:
                next_line_st = diff_text[cur_line + 1][:4]
                assert next_line_st == "diff"
                cur_line += 1
            continue
        else:
            first_char = cur_text[0]
            assert first_char == '+' or first_char == '-'
            file_to_mod_lines_dict[file_nm].append(cur_text)
            cur_line += 1
    return file_to_mod_lines_dict

def get_author_name(commit):
    return git.log(commit, "-1", '--pretty=format:"%an"').replace('\"', '')

def get_author_email(commit):
    return git.log(commit, "-1", '--pretty=format:"%ae"').replace('\"', '')

def get_committer_name(commit):
    return git.log(commit, "-1", '--pretty=format:"%cn"').replace('\"', '')

def get_committer_email(commit):
    return git.log(commit, "-1", '--pretty=format:"%ce"').replace('\"', '')

def get_author_date(commit):
    return git.log(commit, "-1", '--pretty=format:"%ai').replace('\"', '')

def get_commit_date(commit):
    return git.log(commit, "-1", '--pretty=format:"%ci').replace('\"', '')

def get_num_mod_lines(file_to_mod_lines_dict, filter_if = False, filter_loop = False):
    file_to_stats_dict = {}
    
    for file_nm in file_to_mod_lines_dict.keys():
        
        count_dict = [0,0,0] # added, deleted, total
        diff_lines = file_to_mod_lines_dict[file_nm]
        for l in diff_lines:
            if filter_if:
                if "if" not in l.split():
                    continue
            if filter_loop:
                if "for" not in l.split() and "while" not in l.split():
                    continue
                
            if l[:1] == "+":
                count_dict[0] += 1
            elif l[:1] == "-":
                count_dict[1] += 1
            else:
                raise Exception("something wrong!")
        count_dict[2] = count_dict[0] + count_dict[1]
        file_to_stats_dict[file_nm] = tuple(count_dict)
        
    overall_counts = {}
    overall_counts["num_adds"] = sum([t[0] for t in file_to_stats_dict.values()])
    overall_counts["num_dels"] = sum([t[1] for t in file_to_stats_dict.values()])
    overall_counts["num_mod_lns_total"] = sum([t[2] for t in file_to_stats_dict.values()])
    overall_counts["num_mod_files"] = len(file_to_stats_dict.keys())
    
    return file_to_stats_dict, overall_counts

def get_prev_commit(commit):
    commits = git.log(commit, "--oneline", "-2", "--abbrev=40").split("\n")
    if len(commits) == 1:
        return None
    else:
        return commits[1].split()[0]
    
def get_msg(commit):
        return git.log(commit, "-1")
    
merge_commits = {}
def is_merge(commit):
    if commit in merge_commits:
        return True
    
    # shows parents
    if len(git.show("-s", "--pretty=%p", commit).split()) > 1:
        merge_commits[commit] = 1
        return True
    return False


def get_parents(commit):
    return git.show("-s", "--pretty=%p", commit).split()


def get_n_prev_commits(commit, n):
    count = 1
    commits = [commit]
    while count < n:
        prev = get_prev_commit(commit)
        if prev is None:
            return commits
        commits.append(prev)
        commit = prev
        count += 1
    return commits


def find_mod_dirs_sys(files):
    dirs = []
    # files = [f[2:] for f in files] # to remove /b
    for file in files:
        right_ind = file.rfind("/")
        if right_ind == -1:
            dirs.append("/")
        else:
            dirs.append(file[0:right_ind])
    dirs = list(set(dirs))

    subsystems = []
    for file in files:
        left_ind = file.find("/")
        if left_ind == -1:
            dirs.append("/")
        else:
            subsystems.append(file[:left_ind])
    subsystems = list(set(subsystems))
    
    return dirs, subsystems

def get_people_involved(commit):
    msg = get_msg(commit)
    msg_lst = [i.strip() for i in msg.split('\n')]
    people_inv_dict = {}
    
    # TODO: parse spaces to make sure it is indeed a person
    signed_off_lst = [i for i in msg_lst if i.startswith("Signed-off-by:")]
    acked_lst = [i for i in msg_lst if i.startswith("Acked-by:")]
    cc_lst = [i for i in msg_lst if i.startswith("Cc:")]
    reviewed_lst = [i for i in msg_lst if i.startswith("Reviewed-by:")]
    tested_lst = [i for i in msg_lst if i.startswith("Tested-by:")]
    reported_lst = [i for i in msg_lst if i.startswith("Reported-by:")]
    suggested_lst = [i for i in msg_lst if i.startswith("Suggested-by:")]
    fixes_lst = [i for i in msg_lst if (i.startswith("Fixes:") and i != 'Fixes:')] # some are not tags
    co_developed_lst = [i for i in msg_lst if i.startswith("Co-Developed-by:")]
    
    people_inv_dict["signed_off_lst"] = tuple(signed_off_lst)
    people_inv_dict["acked_lst"] = tuple(acked_lst)
    people_inv_dict["cc_lst"] = tuple(cc_lst)
    people_inv_dict["reviewed_lst"] = tuple(reviewed_lst)
    people_inv_dict["tested_lst"] = tuple(tested_lst)
    people_inv_dict["reported_lst"] = tuple(reported_lst)
    people_inv_dict["suggested_lst"] = tuple(suggested_lst)
    people_inv_dict["fixes_lst"] = tuple(fixes_lst)
    people_inv_dict["co_developed_lst"] = tuple(co_developed_lst)
    
    return people_inv_dict


def get_num_mod_fl_dir_sys(info_dict):
    """
    # usage:

    cms = Git.get_all_commits_from(repo, commit = "446279168e030fd0ed68e2bba336bef8bb3da352", max_count = 100)
    dicts = Git.get_info_from_commits(cms)
    dir_num_mod_dict, sys_num_mod_dict = get_num_mod_dir_sys(dicts)
    """

    # info_dict should be a dict of dicts for each commit, i.e. from get_info_from_commits()
    dir_num_mod_dict = {}
    sys_num_mod_dict = {}
    file_num_mod_dict = {}

    for file in info_dict.keys():
        cur_file_lst = info_dict[file]["mod_files_lst"]
        cur_dir_lst = info_dict[file]["mod_dirs"]
        cur_sys_lst = info_dict[file]["mod_sys"]
        
        for cur_file in cur_file_lst:
            # dict membership checking takes O(1) (hashing)
            if cur_file not in file_num_mod_dict:
                file_num_mod_dict[cur_file] = 0
            file_num_mod_dict[cur_file] += 1

        for cur_dir in cur_dir_lst:
            # dict membership checking takes O(1) (hashing)
            if cur_dir not in dir_num_mod_dict:
                dir_num_mod_dict[cur_dir] = 0
            dir_num_mod_dict[cur_dir] += 1

        for cur_sys in cur_sys_lst:        
            if cur_sys not in sys_num_mod_dict:
                sys_num_mod_dict[cur_sys] = 0
            sys_num_mod_dict[cur_sys] += 1
    
    return file_num_mod_dict, dir_num_mod_dict, sys_num_mod_dict

def get_kvfc_from(dicts):
    # commits from get_info_from_commits
    kvfc = []
    for k in dicts.keys():
        if dicts[k]["is_fix"]:
            kvfc.append(dicts[k]["fixes_lst"])
    return kvfc

def get_kvic_from(kvfc):
    """
    # usage:

    cms = Git.get_all_commits_from(repo, commit = "446279168e030fd0ed68e2bba336bef8bb3da352", max_count = 100)
    dicts = Git.get_info_from_commits(cms)

    fc = get_kvfc_from(dicts)
    ic = get_kvic_from(fc)
    """ 

    kvic = []
    
    k = []
    for i in range(len(kvfc)):
        for s in kvfc[i]:
            k.append(s.split()[1])
    full_kvic = [Git.get_commit(i) for i in k]
    return full_kvic


def cal_entropy(file_len_lst):
    entropy = 0.0
    total_lines = sum(file_len_lst)
    for l in file_len_lst:
        if l == 0:
            continue
        pi = l / total_lines
        entropy += pi * math.log2(pi)
    return abs((-1) * entropy)

# sample use case:
def get_commit_info(cur_commit):
    cur_commit_dict = {}

    # cur_commit = "2ea538dbee1c79f6f6c24a6f2f82986e4b7ccb78"
    # cur_commit = "7fedb63a8307dda0ec3b8969a3b233a1dd7ea8e0"
    file_to_mod_lines_dict = get_modified_lines(cur_commit)

    file_to_stats_dict, overall_counts = get_num_mod_lines(file_to_mod_lines_dict, filter_if = 1)
    cur_commit_dict["num_adds_if"] = overall_counts["num_adds"]
    cur_commit_dict["num_dels_if"] = overall_counts["num_dels"]
    cur_commit_dict["num_mod_total_if"] = overall_counts["num_mod_lns_total"]

    file_to_stats_dict, overall_counts = get_num_mod_lines(file_to_mod_lines_dict, filter_loop = 1)
    cur_commit_dict["num_adds_loop"] = overall_counts["num_adds"]
    cur_commit_dict["num_dels_loop"] = overall_counts["num_dels"]
    cur_commit_dict["num_mod_total_loop"] = overall_counts["num_mod_lns_total"]

    file_to_stats_dict, overall_counts = get_num_mod_lines(file_to_mod_lines_dict, filter_if = 0)
    cur_commit_dict["file_hash"] = cur_commit
    cur_commit_dict["num_adds"] = overall_counts["num_adds"]
    cur_commit_dict["num_dels"] = overall_counts["num_dels"]
    cur_commit_dict["num_mod_lns_total"] = overall_counts["num_mod_lns_total"]
    cur_commit_dict["num_mod_files"] = overall_counts["num_mod_files"]
    # cur_commit_dict["msg"] = get_msg(cur_commit)
    cur_commit_dict["is_merge"] = is_merge(cur_commit)
    cur_commit_dict["parents"] = tuple(get_parents(cur_commit))
    cur_commit_dict["mod_files_lst"] = tuple(file_to_stats_dict.keys())

    # added, deleted, total
    cur_commit_dict["entropy"] = cal_entropy([file_to_stats_dict[k][2] for k in file_to_stats_dict.keys()])

    people_inv_dict = get_people_involved(cur_commit)
    cur_commit_dict["ppl_signed_off"] = people_inv_dict["signed_off_lst"]
    cur_commit_dict["ppl_acked"] = people_inv_dict["acked_lst"]
    cur_commit_dict["ppl_cc"] = people_inv_dict["cc_lst"]
    cur_commit_dict["ppl_reviewed"] = people_inv_dict["reviewed_lst"]
    cur_commit_dict["ppl_tested"] = people_inv_dict["tested_lst"]
    cur_commit_dict["ppl_reported"] = people_inv_dict["reported_lst"]
    cur_commit_dict["ppl_suggested"] = people_inv_dict["suggested_lst"]
    cur_commit_dict["ppl_co_developed"] = people_inv_dict["co_developed_lst"]

    cur_commit_dict["fixes_lst"] = people_inv_dict["fixes_lst"]
    cur_commit_dict["is_fix"] = (len(people_inv_dict["fixes_lst"]) > 0)

    dirs, subsystems = find_mod_dirs_sys(cur_commit_dict["mod_files_lst"])                                                         
    cur_commit_dict["mod_dirs"] = tuple(dirs)
    cur_commit_dict["mod_sys"] = tuple(subsystems)
    cur_commit_dict["num_mod_dirs"] = len(dirs)
    cur_commit_dict["num_mod_sys"] = len(subsystems)

    cur_commit_dict["author"] = get_author_name(cur_commit)
    cur_commit_dict["author_email"] = get_author_email(cur_commit)
    cur_commit_dict["committer"] = get_committer_name(cur_commit)
    cur_commit_dict["committer_email"] = get_committer_email(cur_commit)
    cur_commit_dict["author_date"] = get_author_date(cur_commit)
    cur_commit_dict["committer_date"] = get_commit_date(cur_commit)
    
    return cur_commit_dict

def get_info_from_commits(commits):
    from tqdm import tqdm
    com_dict = {}
    for c in commits:
        com_dict[c] = get_commit_info(c)
    return com_dict



