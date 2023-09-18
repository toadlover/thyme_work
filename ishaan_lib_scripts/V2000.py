import sys, os
from multiprocessing import cpu_count, Pool
import os.path


def process(i):
    num = '{0:05d}'.format(i)
    path = "/data/project/thymelab/running_Rosetta/ari_work/REU_shared_space/lib/ftp-rdb-fr.chem-space.com/lib/" + num + "/split"
    if os.path.isfile(path):
        try:
            os.chdir(num)
        except OSError:
            print('NUM ' + num)
            return
        os.system("mv split split.sdf")
        os.system("obabel split.sdf -x2 -O split_new.sdf")
        os.remove("split.sdf")
        os.chdir("..")

    # best to do heavy CPU-bound work here...

    # file write for demonstration


os.chdir("/data/project/thymelab/running_Rosetta/ari_work/REU_shared_space/lib/ftp-rdb-fr.chem-space.com/lib")
temp = os.listdir(".")
l = [int(i) for i in temp]
 
pool = Pool(cpu_count() - 1)
pool.map(process, l)
