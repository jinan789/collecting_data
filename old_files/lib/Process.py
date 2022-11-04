# from multiprocessing import Pool
from pathos.multiprocessing import ProcessingPool as Pool
import multiprocessing
import tqdm


class Multiprocessing:
    def __init__(self, num=1):
        self.process_num = num

    def start_process_pool(self, func, args, task_num):
        with Pool(self.process_num) as p:
            r = list(tqdm.tqdm(p.imap(func, *args), total=task_num))
        return r

# class Lock:
#     def __init__(self):
#         self.lock = multiprocessing.Lock()

#     def get_lock(self):
#         self.lock.acquire()

#     def release_lock(self):
#         self.lock.release()