import sys, os
loc = sys.argv[1]
os.chdir(loc)
for i in os.listdir("."):
    os.chdir(i)
    os.system("mv split split.sdf")
    os.system("obabel split.sdf -x2 -O split_new.sdf")
    os.chdir("..")


