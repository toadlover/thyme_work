#goal of this program is to take in a large mol2 file (thousands of ligands), and break it into mol2 files of up to 1000 ligands
#MUST BE MOL2

import os, sys

ligand_file = sys.argv[1]
base_name = ligand_file.split(".")[0]

#make a directory to output all smaller ligand files
os.system("mkdir " + base_name)

molecule_counter = 0
file_counter = 0

#open the ligand_file
main_file_reader = open(ligand_file, "r")

#make the first sub_file
sub_file = open(base_name + "_" + str(file_counter) + ".mol2", "w")

for line in main_file_reader.readlines():
	
	#count a new ligand when hitting a MOLECULE line
	if "MOLECULE" in line:
		molecule_counter = molecule_counter + 1

		print(file_counter, molecule_counter, line)

	#if molecule count is divisible by 1000, end current file and make a new file
	if molecule_counter % 1000 == 0:
		sub_file.close()
		#increment 1 to file count
		file_counter = file_counter + 1
		#open file using new counter value
		sub_file = open(base_name + "_" + str(file_counter) + ".mol2", "w")

	#write current line to the open sub_file
	sub_file.write(line)

#close final file
sub_file.close()
