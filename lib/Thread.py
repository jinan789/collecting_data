import threading
import Error

thread_num = 1
threads = []

def init(num):
    global thread_num
    thread_num = num

def create_thread(func, argv):
    global threads
    t = threading.Thread(target=func, args=argv)
    threads.append(t)
    # t.setDaemon(True)
    # t.start()

def wait_threads():
    for t in threads:
        t.join()

def start_threads():
    try:
        for i in range(len(threads)):
            threads[i].start()
        wait_threads()
    except:
        raise Exception("Error: Unable to start thread")