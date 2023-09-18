import sys, os

n = 0000
tc = 0
os.mkdir(str("{:04d}".format(n)))
w = open(str("{:04d}".format(n)) + "/split", "w")
with open("Enamine_Diverse_REAL_drug-like_25M_SDF.sdf", "r") as o:
    for line in o:
        if tc == 10000: 
            w.close()
            tc = 0
            n += 1
            os.mkdir(str("{:04d}".format(n)))
            w = open(str("{:04d}".format(n)) + "/split", "w")
        if "$$$$" in line: 
            tc += 1    
        w.write(line)
w.close()
    
