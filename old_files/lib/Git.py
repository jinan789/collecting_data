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



# sample use case:
def get_commit_info(cur_commit):
    cur_commit_dict = {}

    cur_commit_dict["author"] = get_author_name(cur_commit)
    cur_commit_dict["committer"] = get_committer_name(cur_commit)
    cur_commit_dict["author_date"] = get_author_date(cur_commit)
    cur_commit_dict["committer_date"] = get_commit_date(cur_commit)
    
    return cur_commit_dict

def get_info_from_commits(commits):
    from tqdm import tqdm
    com_dict = {}
    for c in commits:
        com_dict[c] = get_commit_info(c)
    return com_dict



