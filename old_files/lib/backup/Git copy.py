import git
import Thread
import time
import sys
from github import Github

class Git():
    # linux_path = "/Users/jinanjiang/Documents/LinuxCommits/linux"

    def __init__(self, repo_path):
        self.repo = git.Repo(repo_path)
        self.git = self.repo.git
        self.g = Github("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")
        self.github_repo = self.g.get_repo("jinan789/linux")

    def reset(self, commit):
        self.git.reset("--hard", commit)

    def get_HEAD(self):
        return self.repo.head.commit

    def initialize_all_commits_from(self, commit = None, max_count = None):
        if commit is None:
            commit = self.get_HEAD().hexsha
        if max_count is None:
            self.all_commits = list(self.repo.iter_commits(commit))
        else:
            self.all_commits = list(repo.iter_commits(commit, max_count = max_count))
        self.all_commits_hash = [c.hexsha for c in self.all_commits]

    def get_previous_commit(self, commit, offset = 1):
        return self.all_commits_hash[self.all_commits_hash.index(commit.hexsha) + offset]

    def get_next_commit(self, commit, offset = 1):
        return self.all_commits_hash[self.all_commits_hash.index(commit.hexsha) - offset]

    def find_github_commit(self, sha):
        return self.github_repo.get_commit(sha=sha)

    def find_num_adds_deletes(self, github_commit):
        del_count = 0
        insert_count = 0
        for file in github_commit.raw_data["files"]:
            del_count += file["deletions"]
            insert_count += file["additions"]
        return {"additions": insert_count, "deletions": del_count, "total_count": insert_count + del_count}

    def find_diff_msg(self, commit, do_print = False):
        prev = self.get_previous_commit(commit)
        msg = self.git.diff(prev, commit, "--word-diff").split("\n")
        
        if do_print:
            for i in msg:
                print(i)
        diff_msg = [i.lstrip() for i in msg if ("{+" in i or "[-" in i)]
        return diff_msg

    def find_num_ifs(self, commit, do_print = False):
        diff_msg = self.find_diff_msg(commit, do_print)
        return len([i for i in diff_msg if "if" in i.split()])

    def get_num_parents(self, commit):
        return len(commit.parents)

    def get_num_parents_many(self, commits):
        counts = []
        for commit in commits:
            counts.append(self.get_num_parents(commit))
        return counts

    def get_added_deleted_lines(self, commit):
        added_lines=[]
        deleted_lines=[]
        for file in commit.raw_data["files"]:
            added_lines.append([i for i in file['patch'].split('\n') if i[0] == '+'])
            deleted_lines.append([i for i in file['patch'].split('\n') if i[0] == '-'])
        return added_lines, deleted_lines

    def get_added_deleted_lines_count(self, commit):
        added_lines, deleted_lines = self.get_added_deleted_lines(commit)
        added_count = 0
        deleted_count = 0
        for f in added_lines:
            added_count += len(f)
        for f in deleted_lines:
            deleted_count += len(f)

        return (added_count, deleted_count)

    def get_added_deleted_lines_count_many(self, commits):
        counts = []
        for commit in commits:
            counts.append(self.get_added_deleted_lines_count(commit))
        return counts

    def get_added_deleted_line_counts_if(self, commit):
        # normalized
        added_lines, deleted_lines = self.get_added_deleted_lines(commit)
        added_if_count = 0
        deleted_if_count = 0
        added_count, deleted_count = self.get_added_deleted_lines_count(commit)
        for f in added_lines:
            added_if_count += len([i.split() for i in f if 'if' in i.split()])
        for f in deleted_lines:
            deleted_if_count += len([i.split() for i in f if 'if' in i.split()])

        if added_count == 0:
            rate_added_if = 0
        else:
            rate_added_if = added_if_count/added_count*10000

        if deleted_count == 0:
            rate_deleted_if = 0
        else:
            rate_deleted_if = deleted_if_count/deleted_count*10000

        return((rate_added_if, rate_deleted_if))

    def get_added_deleted_line_counts_if_many(self, commits):
        counts = []
        for commit in commits:
            counts.append(self.get_added_deleted_line_counts_if(commit))
        return counts

    def get_added_deleted_line_counts_loop(self, commit):

        # normalized
        added_lines, deleted_lines = self.get_added_deleted_lines(commit)
        added_if_count = 0
        deleted_if_count = 0
        added_count, deleted_count = self.get_added_deleted_lines_count(commit)
        for f in added_lines:
            added_if_count += len([i.split() for i in f if ('while' in i.split() or 'for' in i.split())])
        for f in deleted_lines:
            deleted_if_count += len([i.split() for i in f if ('while' in i.split() or 'for' in i.split())])

        if added_count == 0:
            rate_added_if = 0
        else:
            rate_added_if = added_if_count/added_count*10000

        if deleted_count == 0:
            rate_deleted_if = 0
        else:
            rate_deleted_if = deleted_if_count/deleted_count*10000

        return((rate_added_if, rate_deleted_if))

    def get_added_deleted_line_counts_loop_many(self, commits):
        counts = []
        for commit in commits:
            counts.append(self.get_added_deleted_line_counts_loop(commit))
        return counts




















"""
    def find_diff_msg(self, commit, do_print = False):
        prev = self.get_previous_commit(commit)
        msg = self.git.diff(prev, commit, "--word-diff").split("\n")
        
        if do_print:
            for i in msg:
                print(i)
        diff_msg = [i.lstrip() for i in msg if ("{+" in i or "[-" in i)]
        return diff_msg

    def find_num_ifs(self, commit, do_print = False):
        diff_msg = self.find_diff_msg(commit, do_print)
        return len([i for i in diff_msg if "if" in i.split()])

    def find_num_changed_lines(self, commit, do_print = False):
        diff_msg = self.find_diff_msg(commit, do_print)
        return len(diff_msg)

    def find_num_adds_deletes(self, commit, do_print = False):
        diff_msg = self.find_diff_msg(commit, do_print)


        len_add = 0
        len_delete = 0
        for i in diff_msg:
            if "{+" in i and "[-" in i:
                len_add += 1
                len_delete += 1
            elif i[:2] == "[-":
                len_delete += 1
            elif i[:2] == "{+":
                len_add += 1
            else:
                len_add += 1
                len_delete += 1
        return len_add, len_delete

"""

"""

        diff_msg_add = [i for i in diff_msg if "{+" in i]
        diff_msg_delete = [i for i in diff_msg if "[-" in i]
        diff_msg_both = [i for i in diff_msg if ("{+" in diff_msg_add and "[-" in diff_msg_delete)]

        len_add = len(diff_msg_add)
        len_delete = len(diff_msg_delete)
        len_add += len([i for i in diff_msg_delete if (i[:2] != "[-" and i not in diff_msg_both)])
        len_delete += len([i for i in diff_msg_add if (i[:2] != "{+" and i not in diff_msg_both)])

        over_count = len(diff_msg_both)
        len_add += over_count
        len_delete += over_count

        return len_add, len_delete
        """




""""

    def find_num_deletes(self, commit, do_print = False):
        diff_msg = self.find_diff_msg(commit, do_print)
        diff_msg = [i for i in diff_msg if "[-" in i]
        return len(diff_msg)
    
    def get_commit_by_hash(self, hash):
        return self.repo.commit(hash)


    #######################################

    def get_HEAD(self):
        return self.repo.head.commit

    def get_msg(self, commit):
        return commit.message

    def get_author_name(self, commit):
        return commit.author.name

    def get_author_email(self, commit):
        return commit.author.email

    def get_committer_name(self, commit):
        return commit.committer.name

    def get_committer_email(self, commit):
        return commit.committer.email

    def get_author_date(self, commit):
        return commit.authored_date

    def get_commit_date(self, commit):
        return commit.committed_date

"""