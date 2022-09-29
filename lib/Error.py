# -- coding: utf-8 --
import time
import Process

class Error:
    log_path = "err.log"

    def __init__(self, err_log_path="err.log"):
        self.log_path = err_log_path
        # self.lock = Process.Lock()

    ''' 多进程写时加锁，有BUG，会死锁 '''
    # def write_err(self, err_msg_lst):
    #     with self.lock.lock:
    #         with open(self.log_path, "a") as f:
    #             f.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    #             f.write("\n")
    #             for err in err_msg_lst:
    #                 f.write(str(err))
    #                 f.write("\n")
    #             f.write("\n")

    def write_err(self, err_msg_lst):
        with open(self.log_path, "a") as f:
            f.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            f.write("\n")
            for err in err_msg_lst:
                #  f.write(str(err))
                err = str(err).encode("utf8", "replace").decode()
                f.write(err)
                f.write("\n")
            f.write("\n")