import sys, os

loc = sys.argv[1]
n = 00000
tc = 0
os.chdir(loc) 
l = os.listdir(".")
os.mkdir(str("{:05d}".format(n)))
w = open(str("{:05d}".format(n)) + "/split_new.sdf", "w")
for i in l:
    with open(i + "/split_new.sdf", "r") as o:
        for line in o:
            if tc == 500: 
                w.close()
                tc = 0
                n += 1
                os.mkdir(str("{:05d}".format(n)))
                w = open(str("{:05d}".format(n)) + "/split_new.sdf", "w")
            if "$$$$" in line: 
                tc += 1    
            w.write(line)
w.close()
    
