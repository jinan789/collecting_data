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
    
def reset_to_origin():
    reset('0066f1b0e27556381402db3ff31f85d2a2265858')
    
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


def strip_comments(diff_text):

    # one way to simplify things is to preprocess. This also provides reference for other stuff. Also line counts for totals.
    in_file = False
    in_comment = False
    new_file = []
    for cur_l in diff_text:
        #print(cur_l)
        if not in_file:
            if cur_l[:2] == '@@':
                in_file = True
            new_file.append(cur_l)
            continue
        else:
            if cur_l[:4] == 'diff':
                if in_comment:
                    with open("errors.txt", 'a') as f:
                        json.dump('**********' + "       " + commit + '**********', indent=1)
                in_file = False
                new_file.append(cur_l)
                continue

        new_cur_ln = cur_l[0]
        cur_l = cur_l[1:]

        while True:
            # consider //
            #print(cur_l)
            if in_comment:
                dex = cur_l.find('*/')
                if dex == -1:
                    break
                else:
                    in_comment = False
                cur_l = cur_l[dex + 2:]
                if len(cur_l) == 0:
                    break

            else:
                dex = cur_l.find('/*')
                double_bar_dex = cur_l.find('//')

                if dex == -1:
                    if double_bar_dex == -1:
                        new_cur_ln += cur_l
                        break
                    else:
                        cur_l = cur_l[:double_bar_dex]
                        new_cur_ln += cur_l
                        break
                else:
                    # there is /*
                    if double_bar_dex != -1:
                        if double_bar_dex < dex:
                            cur_l = cur_l[:double_bar_dex]
                            new_cur_ln += cur_l
                            break
                        else:
                            in_comment = True
                    else:
                        in_comment = True


                if dex > 0:
                    new_cur_ln += cur_l[:dex]
                cur_l = cur_l[dex:]
                #print(cur_l)
                if len(cur_l) == 0:
                    break


        new_file.append(new_cur_ln)
    return new_file





def get_modified_lines(commit, filter_empty_line = False, filter_comments = False):
    # returns dict
    #    key: filename
    #    value: list of modified lines for this file
    
    diff_text = git.diff(commit+"^1", commit, '-U99999999999999999').split('\n')
        
    if filter_comments:
        diff_text = strip_comments(diff_text)
        
    if filter_empty_line:
        diff_text = [i for i in diff_text if len(i[1:].strip()) != 0]
        
    diff_text = [i for i in diff_text if i.startswith("diff") or i.startswith("+") or i.startswith("-") or i.startswith("@@")]

    
    file_to_mod_lines_dict = {}
    file_nm = None
    
    cur_line = 0
    num_total_lines = len(diff_text)

    
    in_file = True
    while cur_line < num_total_lines:
        cur_text = diff_text[cur_line]

        if cur_text[:4] == 'diff':
            assert in_file
            in_file = False
            file_nm = cur_text.split()[-1]

            if file_nm[:2] == "a/":
                raise Exception("wrong wrong wrong")
            if file_nm[:2] == "b/":
                file_nm = file_nm[2:]


            file_to_mod_lines_dict[file_nm] = []
            cur_line += 1
            continue
            
        elif cur_text[:2] == '@@':
            assert not in_file
            in_file = True
            cur_line += 1
            continue
        else:
            if not in_file:
                cur_line += 1
                continue
            
            first_char = cur_text[0]
            assert first_char == '+' or first_char == '-'
            
            #print(cur_text)
            file_to_mod_lines_dict[file_nm].append(cur_text)
            cur_line += 1
                
        
    return file_to_mod_lines_dict

def get_num_mod_lines(file_to_mod_lines_dict, cur_commit, filter_if = False, filter_loop = False):
    file_to_stats_dict = {}
    
    for file_nm in file_to_mod_lines_dict.keys():
        
        count_dict = [0,0,0] # added, deleted, total
        diff_lines = file_to_mod_lines_dict[file_nm]
        for l in diff_lines:
            if filter_if:
                if "if" not in l.split():
                    continue
                if '(' not in l or ')' not in l:
                    continue
            if filter_loop:
                if "for" not in l.split() and "while" not in l.split():
                    continue
                if '(' not in l or ')' not in l:
                    continue
                
            if l[:1] == '+':
                count_dict[0] += 1
            elif l[:1] == '-':
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
    file_to_mod_lines_dict = get_modified_lines(cur_commit, 1, 1)

    file_to_stats_dict, overall_counts = get_num_mod_lines(file_to_mod_lines_dict, cur_commit, filter_if = 1)
    cur_commit_dict["num_adds_if"] = overall_counts["num_adds"]
    cur_commit_dict["num_dels_if"] = overall_counts["num_dels"]
    cur_commit_dict["num_mod_total_if"] = overall_counts["num_mod_lns_total"]

    file_to_stats_dict, overall_counts = get_num_mod_lines(file_to_mod_lines_dict, cur_commit, filter_loop = 1)
    cur_commit_dict["num_adds_loop"] = overall_counts["num_adds"]
    cur_commit_dict["num_dels_loop"] = overall_counts["num_dels"]
    cur_commit_dict["num_mod_total_loop"] = overall_counts["num_mod_lns_total"]

    file_to_stats_dict, overall_counts = get_num_mod_lines(file_to_mod_lines_dict, cur_commit, filter_if = 0)
    cur_commit_dict["file_hash"] = cur_commit
    cur_commit_dict["num_adds"] = overall_counts["num_adds"]
    cur_commit_dict["num_dels"] = overall_counts["num_dels"]
    cur_commit_dict["num_mod_lns_total"] = overall_counts["num_mod_lns_total"]
    cur_commit_dict["mod_files_lst"] = tuple(file_to_stats_dict.keys())
    
    cur_commit_dict["entropy"] = cal_entropy([file_to_stats_dict[k][2] for k in file_to_stats_dict.keys()])

    
    return cur_commit_dict

def get_info_from_commits(commits):
    from tqdm import tqdm
    com_dict = {}
    for c in commits:
        com_dict[c] = get_commit_info(c)
    return com_dict



