from openbabel import openbabel
from openbabel.pybel import Outputfile, readfile 
import sys, os
import heapq as hq
from heapq import merge
la, ls, li = [], [], []
o = Outputfile("sdf", "final_osort.sdf", overwrite=True)
names = ["a_osort.sdf" , "s_osort.sdf", "i_osort.sdf"]
for f in names:
    for mol in readfile("sdf", f):
        s = float(mol.data["score"])
        t = (s, mol.title, mol)
        if f.startswith("a"):
            la.append(t)
        elif f.startswith("i"):
            li.append(t)
        else:
            ls.append(t)


temp = list(merge(la, ls))
l = list(merge(temp, li))
l = list({tuple(x[1]): x for x in l}.values())
for i in l[0:1000000]:
    o.write(i[2])

o.close()
