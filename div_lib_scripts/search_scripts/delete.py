import os, sys
for i in range(7000, 9000):
    os.system("rm -r ../a/0" + str(i) + "/db.db")
    os.system("rm ../a/0" + str(i) + "/aligned.sdf")
