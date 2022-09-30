import sys
sys.path.append("./lib")
import Git
import os

def test(i):
    os.system("touch testt_" + str(i) + ".txt")
    os.system("git add *")
    os.system("git commit -m \"1\"")
    os.system("git push")

if __name__ == '__main__':
    import multiprocessing as mp

    num_proc = 5
    pool = mp.Pool(num_proc)

    args = []
    for i in range(num_proc):
        args.append(range(num_proc))
    pool.map(test, args)
    pool.close()

