from openbabel import openbabel
from openbabel.pybel import Outputfile, readfile 
import sys, os
import heapq as hq
n = sys.argv[1]
l = []
m = {}
c = 0
print("test1")
o = Outputfile("sdf", n + "_ssort.sdf", overwrite=True)
for dir in os.listdir("../" + n): 
    if not os.path.isfile("../" + n + "/" + dir + "/shits.sdf"):
        continue
    for mol in readfile("sdf", "../" + n + "/" + dir + "/shits.sdf"):
        s = float(mol.data["score"])
        s *= -1
        if len(l) < 100000:
            if s not in m:
                m[s] = [mol]
            else:
                m.get(s).append(mol)
            hq.heappush(l, s)
        elif s < l[0]:
            break
        else:
            old = hq.heappushpop(l, s)
            if len(m.get(old)) > 1:
                m.get(old).pop()
            else:
                del m[old]
            if s not in m:
                m[s] = [mol]
            else:
                m.get(s).append(mol)
    c += 1
    print(c)
print("test2")
l.sort(reverse=True)
print(len(l))
print(len(m),"len m")
temp_l = []
for i in l:
    mols = m.get(i)
    for mol in mols:
        #print(mol)
        if mol not in temp_l:
            o.write(mol)
            temp_l.append(mol)
print("test4")
o.close()
print("test5")
