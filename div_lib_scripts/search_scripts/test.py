from openbabel import openbabel, pybel
from openbabel.pybel import Outputfile, readstring, readfile 
import sys, os
import heapq as hq

for molecule in pybel.readfile("sdf","XGD.sdf"):
    print(molecule.molwt)
