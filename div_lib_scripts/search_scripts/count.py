import sys, os
n = sys.argv[1]
for d in os.listdir("../" + n):
    if not os.path.isdir("../" + n + "/" + d + "/db.db"):
        print(d)
print("done")
'''
w = open("as", "w")
c = 0
for d in os.listdir("../s"):
        o = open("../s/" + d + "/aligned.sdf")
        l = o.read() 
        count = l.count("$$$$")
        w.write(d + " " + str(count) + "\n")
        c += 1 
        if c % 1000 == 0:
            print(c)
w.close()
'''
