import sys, os
#lines 5, 6, 12-17 added for continueation
n = 0000
tc = 0
os.chdir("/data/project/thymelab/running_Rosetta/ari_work/REU_shared_space/lib_25/lib")
os.mkdir(str("{:04d}".format(n)))
w = open(str("{:04d}".format(n)) + "/split", "w")
with open("/data/project/thymelab/running_Rosetta/ari_work/REU_shared_space/lib_25/Enamine_Diverse_REAL_drug-like_25M_SDF.sdf", "r") as o:
    for line in o:
        if tc == 4000: 
            w.close()
            tc = 0
            n += 1
            os.mkdir(str("{:04d}".format(n)))
            w = open(str("{:04d}".format(n)) + "/split", "w")
        if "$$$$" in line: 
            tc += 1    
        w.write(line)
w.close()
    
