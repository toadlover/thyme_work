from multiprocessing import Pool 
import multiprocessing as mp
import sys, os



n = sys.argv[1]
o = open(n + "c", "r")
lines = o.readlines() 

    
print(mp.cpu_count())

def find(line): 
    loc, k = line.split()
    os.system("/data/project/thymelab/running_Rosetta/ari_work/REU_shared_space/test/pharmit-code/src/shapedb/Release/./ShapeDB -NNSearch -k " + k + " -ligand suvorexant.sdf -db /data/project/thymelab/running_Rosetta/ari_work/REU_shared_space/div_lib/" + n + "/" + loc + "/db.db -out /data/project/thymelab/running_Rosetta/ari_work/REU_shared_space/div_lib/" + n + "/" + loc + "/shits.sdf")
if __name__ == '__main__':
    pool = Pool(mp.cpu_count())                       
    pool.map(find, lines)
    
