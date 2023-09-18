import sys, os
#lines 5, 6, 12-17 added for continueation
n = 20001
tc = 0
ic = 0 
b = True
os.chdir("/data/project/thymelab/running_Rosetta/ari_work/REU_shared_space/lib/ftp-rdb-fr.chem-space.com/lib")
os.mkdir(str("{:05d}".format(n)))
w = open(str("{:05d}".format(n)) + "/split", "w")
with open("/data/project/thymelab/running_Rosetta/ari_work/REU_shared_space/lib/ftp-rdb-fr.chem-space.com/Enamine_REAL_lead-like_SDF.sdf", "r") as o:
    for line in o:
        if b:
            if "$$$$" in line:
                ic += 1
                if ic % 1000000 == 0:
                    print(ic)
                if ic == 1000050000:
                    b = False
            continue
 
        if tc == 50000: 
            w.close()
            tc = 0
            n += 1
            if n == 30001:
                sys.exit()
            os.mkdir(str("{:05d}".format(n)))
            w = open(str("{:05d}".format(n)) + "/split", "w")
        if "$$$$" in line: 
            tc += 1    
        w.write(line)
w.close()
    
