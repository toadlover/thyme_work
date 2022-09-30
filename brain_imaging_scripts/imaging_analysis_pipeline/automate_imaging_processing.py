#Ari  Ginsparg
#This program is designed to automate the process of analyzing the zeiss confocal brain imaging data
#This program will use the following user-inputted flags for customization of the run:
#Target parent directory (MANDATORY) - Location that will be used as a root of operations
#Registration image (OPTIONAL) - Option to replace the standard image used in registration with a custom image
#Use custom genotyping (OPTIONAL) - Option to let the use guide the process of genotyping through jobsubmission.sh on their own or let this program do a blanket run of it

import os, sys, argparse

#declare argparse arguments
parser = argparse.ArgumentParser()
parser.add_argument("directory", type=str, help = "Directory that the imaging data is in. Should be full path string (derived from pwd)")
parser.add_argument("register", type=str, help = "Indicate whether you want to run an initial round of registration (if you have a raw dataset, you do, otherwise do false to continue a run that messed up).",  default = "True")
parser.add_argument("-i", type=str, help = "Image used in registration.", default = "/data/project/thymelab/sthyme/stuffonboxbutdonotdelete/imagingscripts/registration/Ref20131120pt14pl2flip.nrrd")
#it seems that just including the flag with any string after makes it true, not using the flag makes it false
parser.add_argument("-g", type=bool, help = "Use custom genotyping (true uses custom, false uses blanket)",  default = False)


#parse args
args = parser.parse_args()

#define location
location = args.directory
#program assumes location input does NOT end with a "/", strip off the slash if it does end with one
if location.endswith("/"):
	temp = location[:-1]
	location = temp

#determine what registration image to use
reg_image = args.i

#determine genotyping protocol
genotyping_proto = args.g

registering = args.register

print("location", "registration image", "custom genotyping protocol", "Do initial registration")
print(location, reg_image, genotyping_proto, registering)

#change to working directory
os.chdir(location)

#in case the directory was created with nrrds stored in images and czis in  czifiles (not completely mandatory), backups to get count of nrrd  numbers
#check contents of czi_files directory
os.system("mkdir czifiles images")
czi_count_int = 0
if czi_count_int == 0:
	os.chdir("czifiles")

	#derive the number of czi files being worked on
	os.system("ls *.czi > czi_file_list.txt")
	czi_files = open("czi_file_list.txt", "r")

	czi_count_int = 0

	for line in czi_files.readlines():
		czi_count_int = czi_count_int + 1 
	czi_files.close()

	#bounce back  to head: 
	os.chdir(location)

if registering == "True":

	#within location move all czi files to z new directory called czifiles, move all nrrd files to a directory called images
	os.system("mkdir czifiles images")

	#derive the number of czi files being worked on
	os.system("ls *.czi > czi_file_list.txt")
	czi_files = open("czi_file_list.txt", "r")

	czi_count_int = 0

	for line in czi_files.readlines():
		czi_count_int = czi_count_int + 1 
	czi_files.close()

	os.system("mv *.czi czifiles")
	os.system("mv *.nrrd images")

	#move a copy of filetodirectory_newstitch.py into images and run it
	os.system("cp /data/project/thymelab/ImagingAnalysis/Zscripts/filetodirectory_newstitch.py images")
	os.chdir("images")

	os.system("python filetodirectory_newstitch.py")

	os.chdir(location)

	#in case the directory was created with nrrds stored in images and czis in  czifiles (not completely mandatory), backups to get count of nrrd  numbers
	#check contents of czi_files directory
	if czi_count_int == 0:
		os.chdir("czifiles")

		#derive the number of czi files being worked on
		os.system("ls *.czi > czi_file_list.txt")
		czi_files = open("czi_file_list.txt", "r")

		czi_count_int = 0

		for line in czi_files.readlines():
			czi_count_int = czi_count_int + 1 
		czi_files.close()

		#bounce back  to head: 
		os.chdir(location)

	#check images directory
	if czi_count_int == 0:
		os.chdir("images")

		#get a count of the number of directories
		os.system("ls -l | grep drw | wc -l > nrrd_dir_count.txt")
		nrrd_dirs = open("nrrd_dir_count.txt", "r")

		czi_count_int = 0

		for line in nrrd_dirs.readlines():
			czi_count_int = int(line.strip("\n")) 
		nrrd_dirs.close()


	if  czi_count_int == 0:
		print("We couldn't detect any czi or nrrd files. Quitting to save from submitting bad jobs")
		quit()

	############### REGISTRATION - make smoothed files and set up architecture for warping
	#write copy of fastqc.slurm and modify it to use desired registration and array range
	fastqc = open("fastqc.slurm", "w")
	fastqc.write("#!/bin/bash\n")
	fastqc.write("#SBATCH -p express # Partition to submit to\n")
	fastqc.write("#SBATCH -n 8 # Number of cores requested\n")
	fastqc.write("#SBATCH -N 1 # Ensure that all cores are on one machine\n")
	fastqc.write("#SBATCH -t 120 # Runtime in minutes\n")
	fastqc.write("#SBATCH --mem=4000 # Memory per cpu in MB (see also --mem-per-cpu)\n")
	fastqc.write("#SBATCH --job-name=arrayJob\n")
	fastqc.write("#SBATCH --array=1-" + str(czi_count_int) + "\n")
	fastqc.write("#SBATCH -o hostname_%A_%a.out # Standard out goes to this file\n")
	fastqc.write("#SBATCH -e hostname_%A_%a.err # Standard err goes to this filehostname\n")
	fastqc.write("module load CMTK/3.3.1\n")
	fastqc.write("munger -b /share/apps/rc/software/CMTK/3.3.1-src/bin/ -T 8 -awr 0102 -X 52 -G 80 -R 3 -A '--accuracy 0.8' -W '--accuracy 1.6' -s " + reg_image + " -d .$SLURM_ARRAY_TASK_ID -v images/$SLURM_ARRAY_TASK_ID/\n")
	fastqc.close()

	#submit script, write line to output file so that the job can be tracked
	os.system("sbatch fastqc.slurm > fastqc_job_id.txt")

	#read fastqc_job_id to get the slurm job id so we can track it in squeue
	fastqc_job_id_file = open("fastqc_job_id.txt", "r")
	fastqc_job_id = ""
	for line in fastqc_job_id_file.readlines():
		fastqc_job_id = line.split()[3].strip("\n")
	fastqc_job_id_file.close()

	#probe squeue with the fastqc id until the id is no longer present (indicating that the job is completely done)
	fastqc_running = True
	while fastqc_running:
		#set fastqc_running to false, will break loop if we don't find a case of the script running
		fastqc_running = False

		#check size of squeue and ensure that slurm timeout error was not hit (if error is hit, file has no contents and derails check)
		status_size = 0
		while status_size == 0:
			#pull contents of squeue
			os.system("squeue > squeue_status.txt")
			os.system("ls -l squeue_status.txt > status_size.txt")
			#read size of status_size
			size_reader = open("status_size.txt", "r")
			for line in size_reader.readlines():
				status_size = int(line.split()[4])
			size_reader.close()
		
		#read contents of squeue and determine if the job is still running
		squeue_reader = open("squeue_status.txt", "r")
		for line in squeue_reader.readlines():
			#set true if we find the job id
			if str(fastqc_job_id) in line:
				fastqc_running = True

		squeue_reader.close()

#done with the first iteration of fastqc, check for any failed jobs (ones that timed out)
os.system("grep \"DUE TO TIME LIMIT\" *err > failed_fastqc_files.txt")

#make a list to determine what needs to be resubmitted
failed_file_ids = []

#read through failed_fastqc_files and pick out the job id numbers
"""
failed_file = open("failed_fastqc_files.txt", "r")
for line in failed_file.readlines():
	bad_id = line.split(".")[0].split("_")[2]
	failed_file_ids.append(str(bad_id))
"""

"""
#check for any .lock files in the registration.* directories
#this indicates that something bad happened and that the directory needs to be re-run
#in theory this shouldn't catch anything, but apparently this is an issue
for r,d,f in os.walk(location):
	#look at list of files in f
	for file in f:
		#if the file is a .lock file, trace the registration and add it to the failed file list if not already in the list
		if file.endswith(".lock"):

			#code from Summer's master.py
			print(file, r)
			failed_file_ids.append(int((file.split('_')[-4])[1:len(file.split('_')[-4])]))
			

			#determine the image it corresponds to (id is between the 3rd and 4th to last underscore in the lock filename)
			
			#lock_id = str(file.split("_")[len(file.split("_")) - 4])

			#add if present
			#if lock_id not in failed_file_ids:
			#	failed_file_ids.append(lock_id)
			
"""

#look down each reformatted folder and see if there are 2 nrrd files. if there are not, need to redo
for r,d,f in os.walk(location):
	for direc in d:
		if direc.startswith("reformatted."):
			#get directory number
			direnum = direc.split(".")[1]

			#determine the number of nrrd files in the directory
			nrrd_files = 0
			for r2,d2,f2 in os.walk(direc):
				for file2 in f2:
					if file2.endswith(".nrrd"):
						nrrd_files = nrrd_files + 1

			#if we do not have 2 files, we need to redo this
			if nrrd_files < 2:
				if str(direnum) not in failed_file_ids:
					failed_file_ids.append(str(direnum))


#resubmit failed jobs for 12 hour run time so they can run to completion (if there are any, check for that)
while len(failed_file_ids) > 0:
	#delete registration and reformatted folders for failed ids
	for b_id in failed_file_ids:
		os.system("rm -dr Registration." + str(b_id) + " reformatted." + str(b_id))	

	#rewrite fastqc.slurm
	os.system("rm fastqc.slurm")

	b_id_string = ""

	#create string of failed file ids to insert into new job
	for b_id in failed_file_ids:
		b_id_string = b_id_string + b_id
		#add comma if not at last
		if b_id != failed_file_ids[len(failed_file_ids) - 1]:
			b_id_string = b_id_string + ","

	fastqc = open("fastqc.slurm", "w")
	fastqc.write("#!/bin/bash\n")
	fastqc.write("#SBATCH -p short # Partition to submit to\n")
	fastqc.write("#SBATCH -n 8 # Number of cores requested\n")
	fastqc.write("#SBATCH -N 1 # Ensure that all cores are on one machine\n")
	fastqc.write("#SBATCH -t 720 # Runtime in minutes\n")
	fastqc.write("#SBATCH --mem=4000 # Memory per cpu in MB (see also --mem-per-cpu)\n")
	fastqc.write("#SBATCH --job-name=arrayJob\n")
	fastqc.write("#SBATCH --array=" + b_id_string + "\n")
	fastqc.write("#SBATCH -o hostname_%A_%a.out # Standard out goes to this file\n")
	fastqc.write("#SBATCH -e hostname_%A_%a.err # Standard err goes to this filehostname\n")
	fastqc.write("module load CMTK/3.3.1\n")
	fastqc.write("munger -b /share/apps/rc/software/CMTK/3.3.1-src/bin/ -T 8 -awr 0102 -X 52 -G 80 -R 3 -A '--accuracy 0.8' -W '--accuracy 1.6' -s " + reg_image + " -d .$SLURM_ARRAY_TASK_ID -v images/$SLURM_ARRAY_TASK_ID/\n")
	fastqc.close()

	#submit new job and track it
	os.system("sbatch fastqc.slurm > fastqc_job_id.txt")
	fastqc_job_id_file = open("fastqc_job_id.txt", "r")
	fastqc_job_id = ""
	for line in fastqc_job_id_file.readlines():
		fastqc_job_id = line.split()[3].strip("\n")
	fastqc_job_id_file.close()

	#probe squeue with the fastqc id until the id is no longer present (indicating that the job is completely done)
	fastqc_running = True
	while fastqc_running:
		#set fastqc_running to false, will break loop if we don't find a case of the script running
		fastqc_running = False

		#check size of squeue and ensure that slurm timeout error was not hit (if error is hit, file has no contents and derails check)
		status_size = 0
		while status_size == 0:
			#pull contents of squeue
			os.system("squeue > squeue_status.txt")
			os.system("ls -l squeue_status.txt > status_size.txt")
			#read size of status_size
			size_reader = open("status_size.txt", "r")
			for line in size_reader.readlines():
				status_size = int(line.split()[4])
			size_reader.close()
		
		#read contents of squeue and determine if the job is still running
		squeue_reader = open("squeue_status.txt", "r")
		for line in squeue_reader.readlines():
			#set true if we find the job id
			if str(fastqc_job_id) in line:
				fastqc_running = True

		squeue_reader.close()

	reformatted_folder_count = 0

	failed_file_ids = []

	#look again for failed runs, and rerun if more failures
	#look down each reformatted folder and see if there are 2 nrrd files. if there are not, need to redo
	for r,d,f in os.walk(location):
		for direc in d:
			if direc.startswith("reformatted."):

				reformatted_folder_count = reformatted_folder_count + 1
				#get directory number
				direnum = direc.split(".")[1]

				#determine the number of nrrd files in the directory
				nrrd_files = 0
				for r2,d2,f2 in os.walk(direc):
					for file2 in f2:
						if file2.endswith(".nrrd"):
							nrrd_files = nrrd_files + 1

				#if we do not have 2 files, we need to redo this
				if nrrd_files < 2:
					if str(direnum) not in failed_file_ids:
						failed_file_ids.append(str(direnum))

	#kill the run if we are somehow missing a reformatted folder (we shouldn't be and I need to figure out why)
	if reformatted_folder_count != czi_count_int:
		print("This is not good, reformatted folder count of " + str(reformatted_folder_count) + " is not equal to the number of czis/images " + str(czi_count_int) +  ". Quitting for manual analysis")
		quit()


#done with initial registration. Move smoothed nrrds to new directory called smoothedtiffs
os.system("mkdir smoothedtiffs")
os.system("mv ./reformatted*/*/*nrrd smoothedtiffs")

############### WARPING - Use created registration infrastructure to create jacobian images

#perform warping smoothing for structure
#gunzip registration files
os.system("gunzip Registration.*/warp/*/*/registration.gz")

#create and run warpingfastqc.slurm
warpingfastqc = open("warpingfastqc_uab.slurm", "w")
warpingfastqc.write("#!/bin/bash\n")
warpingfastqc.write("#SBATCH -p express # Partition to submit to\n")
warpingfastqc.write("#SBATCH -n 1 # Number of cores requested\n")
warpingfastqc.write("#SBATCH -N 1 # Ensure that all cores are on one machine\n")
warpingfastqc.write("#SBATCH -t 60 # Runtime in minutes\n")
warpingfastqc.write("#SBATCH --mem=6000 # Memory per cpu in MB (see also --mem-per-cpu)\n")
warpingfastqc.write("#SBATCH --job-name=arrayJob\n")
warpingfastqc.write("#SBATCH --array=1-" + str(czi_count_int) + "\n")
warpingfastqc.write("#SBATCH -o hostname_%A_%a.out # Standard out goes to this file\n")
warpingfastqc.write("#SBATCH -e hostname_%A_%a.err # Standard err goes to this filehostname\n")
warpingfastqc.write("module load CMTK/3.3.1\n")
warpingfastqc.write("reformatx -o " + location + "/reformatted.$SLURM_ARRAY_TASK_ID/jacobian_$SLURM_ARRAY_TASK_ID.nrrd " + reg_image + " --jacobian " + location + "/Registration.$SLURM_ARRAY_TASK_ID/warp/$SLURM_ARRAY_TASK_ID/*/registration\n")
warpingfastqc.close()

#push the job and get the job id for tracking
os.system("sbatch warpingfastqc_uab.slurm > warpingfastqc_job_id.txt")

#read warpingfastqc_job_id to get the slurm job id so we can track it in squeue
warpingfastqc_job_id_file = open("warpingfastqc_job_id.txt", "r")
warpingfastqc_job_id = ""
for line in warpingfastqc_job_id_file.readlines():
	warpingfastqc_job_id = line.split()[3].strip("\n")
warpingfastqc_job_id_file.close()

#probe squeue with the fastqc id until the id is no longer present (indicating that the job is completely done)
warpingfastqc_running = True
while warpingfastqc_running:
	#set fastqc_running to false, will break loop if we don't find a case of the script running
	warpingfastqc_running = False

	#check size of squeue and ensure that slurm timeout error was not hit (if error is hit, file has no contents and derails check)
	status_size = 0
	while status_size == 0:
		#pull contents of squeue
		os.system("squeue > squeue_status.txt")
		os.system("ls -l squeue_status.txt > status_size.txt")
		#read size of status_size
		size_reader = open("status_size.txt", "r")
		for line in size_reader.readlines():
			status_size = int(line.split()[4])
		size_reader.close()
	
	#read contents of squeue and determine if the job is still running
	squeue_reader = open("squeue_status.txt", "r")
	for line in squeue_reader.readlines():
		#set true if we find the job id
		if str(warpingfastqc_job_id) in line:
			warpingfastqc_running = True

	squeue_reader.close()

#make sure all warped files are created reformatted*/jacobian*.nrrd
#need to rerun for any that fail

failed_file_ids = []

#look down each reformatted folder and see if there are 1 nrrd files. if there are not, need to redo
for r,d,f in os.walk(location):
	for direc in d:
		if direc.startswith("reformatted."):
			#get directory number
			direnum = direc.split(".")[1]

			#determine the number of nrrd files in the directory
			nrrd_files = 0
			for r2,d2,f2 in os.walk(direc):
				for file2 in f2:
					if file2.endswith(".nrrd"):
						nrrd_files = nrrd_files + 1

			#if we do not have 1 files, we need to redo this
			if nrrd_files < 1:
				if str(direnum) not in failed_file_ids:
					failed_file_ids.append(str(direnum))

#variable to hold count of jacobian files, should equal number of czi files; value may be different if we have failed file ids (and value will correspondingly change)
jacobian_count = czi_count_int

#rerun warping for any failures
#resubmit failed jobs for 12 hour run time so they can run to completion (if there are any, check for that)
while len(failed_file_ids) > 0:
	#delete registration and reformatted folders for failed ids
	for b_id in failed_file_ids:
		os.system("rm -dr reformatted." + str(b_id) + "/*")	

	#rewrite fastqc.slurm
	os.system("rm warpingfastqc_uab.slurm")

	b_id_string = ""

	#create string of failed file ids to insert into new job
	for b_id in failed_file_ids:
		b_id_string = b_id_string + b_id
		#add comma if not at last
		if b_id != failed_file_ids[len(failed_file_ids) - 1]:
			b_id_string = b_id_string + ","

	warpingfastqc = open("warpingfastqc_uab.slurm", "w")
	warpingfastqc.write("#!/bin/bash\n")
	warpingfastqc.write("#SBATCH -p short # Partition to submit to\n")
	warpingfastqc.write("#SBATCH -n 1 # Number of cores requested\n")
	warpingfastqc.write("#SBATCH -N 1 # Ensure that all cores are on one machine\n")
	warpingfastqc.write("#SBATCH -t 720 # Runtime in minutes\n")
	warpingfastqc.write("#SBATCH --mem=6000 # Memory per cpu in MB (see also --mem-per-cpu)\n")
	warpingfastqc.write("#SBATCH --job-name=arrayJob\n")
	warpingfastqc.write("#SBATCH --array=1-" + str(czi_count_int) + "\n")
	warpingfastqc.write("#SBATCH -o hostname_%A_%a.out # Standard out goes to this file\n")
	warpingfastqc.write("#SBATCH -e hostname_%A_%a.err # Standard err goes to this filehostname\n")
	warpingfastqc.write("module load CMTK/3.3.1\n")
	warpingfastqc.write("reformatx -o " + location + "/reformatted.$SLURM_ARRAY_TASK_ID/jacobian_$SLURM_ARRAY_TASK_ID.nrrd " + reg_image + " --jacobian " + location + "/Registration.$SLURM_ARRAY_TASK_ID/warp/$SLURM_ARRAY_TASK_ID/*/registration\n")
	warpingfastqc.close()

	#submit new job and track it
	os.system("sbatch warpingfastqc_uab.slurm > warpingfastqc_job_id.txt")
	fastqc_job_id_file = open("warpingfastqc_job_id.txt", "r")
	fastqc_job_id = ""
	for line in fastqc_job_id_file.readlines():
		fastqc_job_id = line.split()[3].strip("\n")
	fastqc_job_id_file.close()
	#probe squeue with the fastqc id until the id is no longer present (indicating that the job is completely done)
	fastqc_running = True
	while fastqc_running:
		#set fastqc_running to false, will break loop if we don't find a case of the script running
		fastqc_running = False

		#check size of squeue and ensure that slurm timeout error was not hit (if error is hit, file has no contents and derails check)
		status_size = 0
		while status_size == 0:
			#pull contents of squeue
			os.system("squeue > squeue_status.txt")
			os.system("ls -l squeue_status.txt > status_size.txt")
			#read size of status_size
			size_reader = open("status_size.txt", "r")
			for line in size_reader.readlines():
				status_size = int(line.split()[4])
			size_reader.close()
		
		#read contents of squeue and determine if the job is still running
		squeue_reader = open("squeue_status.txt", "r")
		for line in squeue_reader.readlines():
			#set true if we find the job id
			if str(fastqc_job_id) in line:
				fastqc_running = True

		squeue_reader.close()



	jacobian_count = 0

	failed_file_ids = []

	#look again for failed runs, and rerun if more failures
	#look down each reformatted folder and see if there are 2 nrrd files. if there are not, need to redo
	for r,d,f in os.walk(location):
		for direc in d:
			if direc.startswith("reformatted."):

				#get directory number
				direnum = direc.split(".")[1]

				#determine the number of nrrd files in the directory
				nrrd_files = 0
				for r2,d2,f2 in os.walk(direc):
					for file2 in f2:
						if file2.endswith(".nrrd") and file2.startswith("jacobian"):
							nrrd_files = nrrd_files + 1
							jacobian_count = jacobian_count + 1

				#if we do not have 2 files, we need to redo this
				if nrrd_files < 1:
					if str(direnum) not in failed_file_ids:
						failed_file_ids.append(str(direnum))

#kill the run if we are somehow missing a reformatted folder (we shouldn't be and I need to figure out why)
if jacobian_count != czi_count_int:
	print("This is not good, jacobian count of " + str(jacobian_count) + " is not equal to the number of czis/images " + str(czi_count_int) + ". Quitting for manual analysis")
	quit()

#create directory warpingsmoothed to put jacobian images in
os.system("mkdir warpingsmoothed")
#move jacobian files into warpingsmoothed
os.system("mv reformatted.*/jacobian* warpingsmoothed")

#delete hostname files
os.system("rm host*")

############### ACTIVITY SMOOTHING - Smoothing step for activity analysis, creates smoothed tiff files from nrrds

#move to smoothedtiffs
os.chdir(location + "/smoothedtiffs")

#get the pattern for the nrrd file names for fastqc_smoothing
#write present nrrd files to a file to read
os.system("ls *.nrrd > nrrd_file_names.txt")
#read file and get the first nrrd name to derive the pattern
#this assumes the file name works like (variable pattern)_id#_01/02_warp_m0g80c4e1e-1x52r3.nrrd
#assuming this, pattern is everything located before the 4th to last underscore
pattern = ""
nrrd_file = open("nrrd_file_names.txt", "r")
for line in nrrd_file.readlines():
	underscore_breakup = line.split("_")
	#build pattern by putting it together until hitting the 4th to last underscore
	underscore_counter = 0
	while True:
		pattern = pattern + underscore_breakup[underscore_counter] + "_"

		underscore_counter = underscore_counter + 1
		
		if underscore_counter == (len(underscore_breakup) - 4):
			break

		
	break
nrrd_file.close()

#make fastqc_smoothing.slurm script
warpingfastqc = open("fastqc_smoothing.slurm", "w")
warpingfastqc.write("#!/bin/bash\n")
warpingfastqc.write("#SBATCH -p express # Partition to submit to\n")
warpingfastqc.write("#SBATCH -n 1 # Number of cores requested\n")
warpingfastqc.write("#SBATCH -N 1 # Ensure that all cores are on one machine\n")
warpingfastqc.write("#SBATCH -t 3 # Runtime in minutes\n")
warpingfastqc.write("#SBATCH --mem=8000 # Memory per cpu in MB (see also --mem-per-cpu)\n")
warpingfastqc.write("#SBATCH --job-name=arrayJob\n")
warpingfastqc.write("#SBATCH --array=1-" + str(czi_count_int) + "\n")
warpingfastqc.write("#SBATCH -o hostname_%A_%a.out # Standard out goes to this file\n")
warpingfastqc.write("#SBATCH -e hostname_%A_%a.err # Standard err goes to this filehostname\n")
warpingfastqc.write("module load Fiji/20201104-1356\n")
warpingfastqc.write("echo `hostname`\n")
warpingfastqc.write("STUB_FILE=`echo ls /tmp/ImageJ-$USER*.stub`\n")
warpingfastqc.write("if [[ $STUB_FILE ]]; then rm -f /tmp/ImageJ-$USER*.stub; fi\n")
warpingfastqc.write("xvfb-run -d ImageJ-linux64 -macro /data/project/thymelab/FijiScripts/PrepareStacksForMAPMapping_cluster.m \" " + pattern + "$SLURM_ARRAY_TASK_ID warp_m0g80c4e1e-1x52r3.nrrd " + location + "/smoothedtiffs/\"\n")
warpingfastqc.close()

#push the job and get the job id for tracking
os.system("sbatch fastqc_smoothing.slurm > fastqc_smoothing.txt")

#read warpingfastqc_job_id to get the slurm job id so we can track it in squeue
fastqc_smoothing_job_id_file = open("fastqc_smoothing.txt", "r")
fastqc_smoothing_job_id = ""
for line in fastqc_smoothing_job_id_file.readlines():
	fastqc_smoothing_job_id = line.split()[3].strip("\n")
fastqc_smoothing_job_id_file.close()

#probe squeue with the fastqc id until the id is no longer present (indicating that the job is completely done)
fastqc_smoothing_running = True
while fastqc_smoothing_running:
	#set fastqc_running to false, will break loop if we don't find a case of the script running
	fastqc_smoothing_running = False

	#check size of squeue and ensure that slurm timeout error was not hit (if error is hit, file has no contents and derails check)
	status_size = 0
	while status_size == 0:
		#pull contents of squeue
		os.system("squeue > squeue_status.txt")
		os.system("ls -l squeue_status.txt > status_size.txt")
		#read size of status_size
		size_reader = open("status_size.txt", "r")
		for line in size_reader.readlines():
			status_size = int(line.split()[4])
		size_reader.close()
	
	#read contents of squeue and determine if the job is still running
	squeue_reader = open("squeue_status.txt", "r")
	for line in squeue_reader.readlines():
		#set true if we find the job id
		if str(fastqc_smoothing_job_id) in line:
			fastqc_smoothing_running = True

	squeue_reader.close()

#make a list to hold any smoothed tiffs that may have failed
bad_tiff_files = []

#look at file size of tiff files, if the size is 0, then it is a bad tiff
os.system("ls -l *tiff > tiff_files.txt")

#create dictionary to count to make sure that we have 2 tiffs for each index (if we don't, this is a bad id and we need to rerun)
tiff_dict = {}
for i in range(1, czi_count_int + 1):
	tiff_dict[i] = 0

#read tiff_files and identify the file size of the tiff tiles
tiff_file = open("tiff_files.txt", "r")
for line in tiff_file.readlines():
	size = str(line.split(" ")[4])
	file_id = str(line.split(" ")[8].split("_")[len(line.split(" ")[8].split("_")) - 4])

	tiff_dict[int(file_id)] = tiff_dict[int(file_id)] + 1

	#if size is 0, file is bad
	#delete file and add file id to list
	if size == "0":
		os.system("rm " + line.split(" ")[8])
		
		bad_tiff_files.append(file_id)

#if fewer than 2 tiff files for an index, consider it bad
for i in range(1, czi_count_int + 1):
	if tiff_dict[i] != 2 and str(i) not in bad_tiff_files:
		bad_tiff_files.append(str(i))

#make a string out of all the bad files (if there are any) and submit in a new job
while len(bad_tiff_files) > 0:
	bad_tiff_string = ""
	for badtiff in bad_tiff_files:
		bad_tiff_string = badtiff + "," + bad_tiff_string

	#rewrite the slurm file for only the bad tiffs
	#make fastqc_smoothing.slurm script
	warpingfastqc = open("fastqc_smoothing.slurm", "w")
	warpingfastqc.write("#!/bin/bash\n")
	warpingfastqc.write("#SBATCH -p express # Partition to submit to\n")
	warpingfastqc.write("#SBATCH -n 1 # Number of cores requested\n")
	warpingfastqc.write("#SBATCH -N 1 # Ensure that all cores are on one machine\n")
	warpingfastqc.write("#SBATCH -t 4 # Runtime in minutes\n")
	warpingfastqc.write("#SBATCH --mem=8000 # Memory per cpu in MB (see also --mem-per-cpu)\n")
	warpingfastqc.write("#SBATCH --job-name=arrayJob\n")
	warpingfastqc.write("#SBATCH --array=" + bad_tiff_string + "\n")
	warpingfastqc.write("#SBATCH -o hostname_%A_%a.out # Standard out goes to this file\n")
	warpingfastqc.write("#SBATCH -e hostname_%A_%a.err # Standard err goes to this filehostname\n")
	warpingfastqc.write("module load Fiji/20201104-1356\n")
	warpingfastqc.write("echo `hostname`\n")
	warpingfastqc.write("STUB_FILE=`echo ls /tmp/ImageJ-$USER*.stub`\n")
	warpingfastqc.write("if [[ $STUB_FILE ]]; then rm -f /tmp/ImageJ-$USER*.stub; fi\n")
	warpingfastqc.write("xvfb-run -d ImageJ-linux64 -macro /data/project/thymelab/FijiScripts/PrepareStacksForMAPMapping_cluster.m \" " + pattern + "$SLURM_ARRAY_TASK_ID warp_m0g80c4e1e-1x52r3.nrrd " + location + "/smoothedtiffs/\"\n")
	warpingfastqc.close()

	#push the job and get the job id for tracking
	os.system("sbatch fastqc_smoothing.slurm > fastqc_smoothing.txt")

	#read warpingfastqc_job_id to get the slurm job id so we can track it in squeue
	fastqc_smoothing_job_id_file = open("fastqc_smoothing.txt", "r")
	fastqc_smoothing_job_id = ""
	for line in fastqc_smoothing_job_id_file.readlines():
		fastqc_smoothing_job_id = line.split()[3].strip("\n")
	fastqc_smoothing_job_id_file.close()

	#probe squeue with the fastqc id until the id is no longer present (indicating that the job is completely done)
	fastqc_smoothing_running = True
	while fastqc_smoothing_running:
		#set fastqc_running to false, will break loop if we don't find a case of the script running
		fastqc_smoothing_running = False

		#check size of squeue and ensure that slurm timeout error was not hit (if error is hit, file has no contents and derails check)
		status_size = 0
		while status_size == 0:
			#pull contents of squeue
			os.system("squeue > squeue_status.txt")
			os.system("ls -l squeue_status.txt > status_size.txt")
			#read size of status_size
			size_reader = open("status_size.txt", "r")
			for line in size_reader.readlines():
				status_size = int(line.split()[4])
			size_reader.close()
		
		#read contents of squeue and determine if the job is still running
		squeue_reader = open("squeue_status.txt", "r")
		for line in squeue_reader.readlines():
			#set true if we find the job id
			if str(fastqc_smoothing_job_id) in line:
				fastqc_smoothing_running = True

		squeue_reader.close()

	#make a list to hold any smoothed tiffs that may have failed
	bad_tiff_files = []

	#look at file size of tiff files, if the size is 0, then it is a bad tiff
	os.system("ls -l *tiff > tiff_files.txt")

	#create dictionary to count to make sure that we have 2 tiffs for each index (if we don't, this is a bad id and we need to rerun)
	tiff_dict = {}
	for i in range(1, czi_count_int + 1):
		tiff_dict[i] = 0

	#read tiff_files and identify the file size of the tiff tiles
	tiff_file = open("tiff_files.txt", "r")
	for line in tiff_file.readlines():
		size = str(line.split(" ")[4])
		file_id = str(line.split(" ")[8].split("_")[len(line.split(" ")[8].split("_")) - 4])

		tiff_dict[int(file_id)] = tiff_dict[int(file_id)] + 1

		#if size is 0, file is bad
		#delete file and add file id to list
		if size == "0":
			os.system("rm " + line.split(" ")[8])
			
			bad_tiff_files.append(file_id)

	#if fewer than 2 tiff files for an index, consider it bad
	for i in range(1, czi_count_int + 1):
		if tiff_dict[i] != 2 and str(i) not in bad_tiff_files:
			bad_tiff_files.append(str(i))

#job is done running, should have tiff files now. move to onlysmoothedtiffs directory (likely made, but we will try anyway)
os.system("mkdir onlysmoothedtiffs")
os.system("mv *.tiff onlysmoothedtiffs")

#delete hostname files
os.system("rm host*")

#we'll come back at the end for working with the contents of onlysmoothedtiffs if the user requests it
############### STRUCTURE SMOOTHING - make tiffs of smoothed structure nrrds
#move to warpingsmoothed to make tiffs of the jacobian files
os.chdir(location + "/warpingsmoothed")

#make warpingfastqc_smoothing_uab.slurm
warpingfastqcsmoothing = open("warpingfastqc_smoothing.slurm", "w")
warpingfastqcsmoothing.write("#!/bin/bash\n")
warpingfastqcsmoothing.write("#SBATCH -p express # Partition to submit to\n")
warpingfastqcsmoothing.write("#SBATCH -n 1 # Number of cores requested\n")
warpingfastqcsmoothing.write("#SBATCH -N 1 # Ensure that all cores are on one machine\n")
warpingfastqcsmoothing.write("#SBATCH -t 4 # Runtime in minutes\n")
warpingfastqcsmoothing.write("#SBATCH --mem=8000 # Memory per cpu in MB (see also --mem-per-cpu)\n")
warpingfastqcsmoothing.write("#SBATCH --job-name=arrayJob\n")
warpingfastqcsmoothing.write("#SBATCH --array=1-" + str(czi_count_int) + "\n")
warpingfastqcsmoothing.write("#SBATCH -o hostname_%A_%a.out # Standard out goes to this file\n")
warpingfastqcsmoothing.write("#SBATCH -e hostname_%A_%a.err # Standard err goes to this filehostname\n")
warpingfastqcsmoothing.write("module load Fiji/20201104-1356\n")
warpingfastqcsmoothing.write("echo `hostname`\n")
warpingfastqcsmoothing.write("STUB_FILE=`echo ls /tmp/ImageJ-$USER*.stub`\n")
warpingfastqcsmoothing.write("if [[ $STUB_FILE ]]; then rm -f /tmp/ImageJ-$USER*.stub; fi\n")
warpingfastqcsmoothing.write("xvfb-run -d ImageJ-linux64 -macro /data/project/thymelab/FijiScripts/PrepareJacobianStacksForMAPMapping_cluster.m \"jacobian_$SLURM_ARRAY_TASK_ID.nrrd " + location + "/warpingsmoothed/\"\n")
warpingfastqcsmoothing.close()

#push the job and get the job id for tracking
os.system("sbatch warpingfastqc_smoothing.slurm > fastqc_smoothing.txt")

#read warpingfastqc_job_id to get the slurm job id so we can track it in squeue
fastqc_smoothing_job_id_file = open("fastqc_smoothing.txt", "r")
fastqc_smoothing_job_id = ""
for line in fastqc_smoothing_job_id_file.readlines():
	fastqc_smoothing_job_id = line.split()[3].strip("\n")
fastqc_smoothing_job_id_file.close()

#probe squeue with the fastqc id until the id is no longer present (indicating that the job is completely done)
fastqc_smoothing_running = True
while fastqc_smoothing_running:
	#set fastqc_running to false, will break loop if we don't find a case of the script running
	fastqc_smoothing_running = False

	#check size of squeue and ensure that slurm timeout error was not hit (if error is hit, file has no contents and derails check)
	status_size = 0
	while status_size == 0:
		#pull contents of squeue
		os.system("squeue > squeue_status.txt")
		os.system("ls -l squeue_status.txt > status_size.txt")
		#read size of status_size
		size_reader = open("status_size.txt", "r")
		for line in size_reader.readlines():
			status_size = int(line.split()[4])
		size_reader.close()
	
	#read contents of squeue and determine if the job is still running
	squeue_reader = open("squeue_status.txt", "r")
	for line in squeue_reader.readlines():
		#set true if we find the job id
		if str(fastqc_smoothing_job_id) in line:
			fastqc_smoothing_running = True

	squeue_reader.close()

#Ensure all jacobian tiffs were made and redo generation for any failed attempts
#make a list to hold any smoothed tiffs that may have failed
bad_tiff_files = []

#look at file size of tiff files, if the size is 0, then it is a bad tiff
os.system("ls -l *tiff > tiff_files.txt")

#create dictionary to count to make sure that we have 2 tiffs for each index (if we don't, this is a bad id and we need to rerun)
tiff_dict = {}
for i in range(1, czi_count_int + 1):
	tiff_dict[i] = 0

#read tiff_files and identify the file size of the tiff tiles
tiff_file = open("tiff_files.txt", "r")
for line in tiff_file.readlines():
	size = str(line.split(" ")[4])
	file_id = str(line.split(" ")[8].split("_")[1].split(".")[0])

	tiff_dict[int(file_id)] = tiff_dict[int(file_id)] + 1

	#if size is 0, file is bad
	#delete file and add file id to list
	if size == "0":
		os.system("rm " + line.split(" ")[8])
		
		bad_tiff_files.append(file_id)

#if fewer than 2 tiff files for an index, consider it bad
for i in range(1, czi_count_int + 1):
	if tiff_dict[i] != 1 and str(i) not in bad_tiff_files:
		bad_tiff_files.append(str(i))

#make a string out of all the bad files (if there are any) and submit in a new job
while len(bad_tiff_files) > 0:
	bad_tiff_string = ""
	for badtiff in bad_tiff_files:
		bad_tiff_string = badtiff + "," + bad_tiff_string

	#rewrite the slurm file for only the bad tiffs
	#make fastqc_smoothing.slurm script
	warpingfastqcsmoothing = open("warpingfastqc_smoothing.slurm", "w")
	warpingfastqcsmoothing.write("#!/bin/bash\n")
	warpingfastqcsmoothing.write("#SBATCH -p express # Partition to submit to\n")
	warpingfastqcsmoothing.write("#SBATCH -n 1 # Number of cores requested\n")
	warpingfastqcsmoothing.write("#SBATCH -N 1 # Ensure that all cores are on one machine\n")
	warpingfastqcsmoothing.write("#SBATCH -t 4 # Runtime in minutes\n")
	warpingfastqcsmoothing.write("#SBATCH --mem=8000 # Memory per cpu in MB (see also --mem-per-cpu)\n")
	warpingfastqcsmoothing.write("#SBATCH --job-name=arrayJob\n")
	warpingfastqcsmoothing.write("#SBATCH --array=" + bad_tiff_string + "\n")
	warpingfastqcsmoothing.write("#SBATCH -o hostname_%A_%a.out # Standard out goes to this file\n")
	warpingfastqcsmoothing.write("#SBATCH -e hostname_%A_%a.err # Standard err goes to this filehostname\n")
	warpingfastqcsmoothing.write("module load Fiji/20201104-1356\n")
	warpingfastqcsmoothing.write("echo `hostname`\n")
	warpingfastqcsmoothing.write("STUB_FILE=`echo ls /tmp/ImageJ-$USER*.stub`\n")
	warpingfastqcsmoothing.write("if [[ $STUB_FILE ]]; then rm -f /tmp/ImageJ-$USER*.stub; fi\n")
	warpingfastqcsmoothing.write("xvfb-run -d ImageJ-linux64 -macro /data/project/thymelab/FijiScripts/PrepareJacobianStacksForMAPMapping_cluster.m \"jacobian_$SLURM_ARRAY_TASK_ID.nrrd " + location + "/warpingsmoothed/\"\n")
	warpingfastqcsmoothing.close()

	#push the job and get the job id for tracking
	os.system("sbatch warpingfastqc_smoothing.slurm > fastqc_smoothing.txt")

	#read warpingfastqc_job_id to get the slurm job id so we can track it in squeue
	fastqc_smoothing_job_id_file = open("fastqc_smoothing.txt", "r")
	fastqc_smoothing_job_id = ""
	for line in fastqc_smoothing_job_id_file.readlines():
		fastqc_smoothing_job_id = line.split()[3].strip("\n")
	fastqc_smoothing_job_id_file.close()

	#probe squeue with the fastqc id until the id is no longer present (indicating that the job is completely done)
	fastqc_smoothing_running = True
	while fastqc_smoothing_running:
		#set fastqc_running to false, will break loop if we don't find a case of the script running
		fastqc_smoothing_running = False

		#check size of squeue and ensure that slurm timeout error was not hit (if error is hit, file has no contents and derails check)
		status_size = 0
		while status_size == 0:
			#pull contents of squeue
			os.system("squeue > squeue_status.txt")
			os.system("ls -l squeue_status.txt > status_size.txt")
			#read size of status_size
			size_reader = open("status_size.txt", "r")
			for line in size_reader.readlines():
				status_size = int(line.split()[4])
			size_reader.close()
		
		#read contents of squeue and determine if the job is still running
		squeue_reader = open("squeue_status.txt", "r")
		for line in squeue_reader.readlines():
			#set true if we find the job id
			if str(fastqc_smoothing_job_id) in line:
				fastqc_smoothing_running = True

		squeue_reader.close()

	#make a list to hold any smoothed tiffs that may have failed
	bad_tiff_files = []

	#look at file size of tiff files, if the size is 0, then it is a bad tiff
	os.system("ls -l *tiff > tiff_files.txt")

	#create dictionary to count to make sure that we have 2 tiffs for each index (if we don't, this is a bad id and we need to rerun)
	tiff_dict = {}
	for i in range(1, czi_count_int + 1):
		tiff_dict[i] = 0

	#read tiff_files and identify the file size of the tiff tiles
	tiff_file = open("tiff_files.txt", "r")
	for line in tiff_file.readlines():
		size = str(line.split(" ")[4])
		file_id = str(line.split(" ")[8].split("_")[1].split(".")[0])

		tiff_dict[int(file_id)] = tiff_dict[int(file_id)] + 1

		#if size is 0, file is bad
		#delete file and add file id to list
		if size == "0":
			os.system("rm " + line.split(" ")[8])
			
			bad_tiff_files.append(file_id)

	#if fewer than 2 tiff files for an index, consider it bad
	for i in range(1, czi_count_int + 1):
		if tiff_dict[i] != 1 and str(i) not in bad_tiff_files:
			bad_tiff_files.append(str(i))

#we should have jacobian tiffs now too, make an onlysmoothedtiffs directory
os.system("mkdir onlysmoothedtiffs")
os.system("mv *.tiff onlysmoothedtiffs")

#delete hostname files
os.system("rm host*")

#now go through and run genotyping analysis if desired (you need to use the flag)
#quit if not selected
if genotyping_proto == False:
	quit()

#for genotpying analyses, will use all groups present in the matrix
#matrix needs to be present in respective directories by this point, or it will fail
############### ACTIVITY GENOTYPING AND ANALYSIS
#go to the activity onlysmoothedtiffs first
os.chdir(location + "/smoothedtiffs/onlysmoothedtiffs")

#copy all relevant Make*.m and  split*.py files
os.system("cp /data/project/thymelab/ImagingAnalysis/Zscripts/Make*.m " + location + "/smoothedtiffs/onlysmoothedtiffs")
os.system("cp /data/project/thymelab/ImagingAnalysis/Zscripts/splitgenotypes_doubleoption_addvalue_updated.py /data/project/thymelab/ImagingAnalysis/Zscripts/splitfilesbygenotypecomma_setupfiles_bothlsmandczi_updated.py " + location + "/smoothedtiffs/onlysmoothedtiffs")

#run split genotypes
os.system("python splitgenotypes_doubleoption_addvalue_updated.py")

#edit genotyping file so that all groups are included in final analysis
genotyping_file = open("genotyping", "r")
new_genotyping_file = open("new_genotyping", "w")

#run through lines of genotyping, add an asterisk in  front of comparison lines, and write to new_genotyping
#skip first line
line_counter = 1
for line in  genotyping.readlines():
	if line_counter == 1:
		line_counter = line_counter + 1
		new_genotyping_file.write(line)
		continue
	#take line and  put an  asterisk at the front, write to new_genotyping_file
	new_genotyping_file.write("*" + line)

genotyping_file.close()
new_genotyping_file.close()

#overwrite genotyping with contents of new_genotyping
os.system("mv new_genotyping genotyping")

#run splitfiles
os.system("python splitfilesbygenotypecomma_setupfiles_bothlsmandczi_updated.py")

#should now have jobsubmission.sh
#we won't run it directly, because we can run  it faster
#we will submit each job in the file, and read the out file to know when we can submit the next file
job_file =  open("jobsubmission.sh", "r")

for line in job_file.readlines():
	#only work with sbatch lines
	if line.startswith("sbatch"):
		#strip the newline off the line
		line_string = line.strip("\n")

		#add to string to allow for storing the job id
		line_string = line_string + " > analysis_job_info.txt"

		#submit the job and track the job id
		os.system(line_string)

		analysis_job_id_file = open("analysis_job_info.txt", "r")
		analysis_job_id = ""
		for line in analysis_job_id_file.readlines():
			analysis_job_id = line.split()[3].strip("\n")
		analysis_job_id_file.close()

		#track the outfile until the job starts analyzing (allowing for parallel  work, jobs die if they try to run in parallel  if they start at the same time)
		job_going = False
		while job_going == False:
			#check if string "Analyzing and transferring" is in the out file and only quit the loop  if it is (we are good to move one at this point)
			os.system("grep \"Analyzing and transferring\" host*" + str(analysis_job_id) + "*.out > analysis_grep.txt")

			#read analysis_grep.txt and see if the line is present, if so we can end the loop
			grep_a = open("analysis_grep.txt", "r")
			for line in grep_a.readlines():
				if "Analyzing and transferring" in line:
					job_going = True
			grep_a.close()

job_file.close()
#all analysis jobs have been pushed now

#delete hostname files
os.system("rm host*")

############### STRUCTURE GENOTYPING AND ANALYSIS
#go to the structure onlysmoothedtiffs 
os.chdir(location + "/warpingsmoothed/onlysmoothedtiffs")

#copy all relevant Make*.m and  split*.py files
os.system("cp /data/project/thymelab/ImagingAnalysis/Zscripts/Make*.m " + location + "/warpingsmoothed/onlysmoothedtiffs")
os.system("cp /data/project/thymelab/ImagingAnalysis/Zscripts/splitgenotypes_doubleoption_addvalue_updated.py /data/project/thymelab/ImagingAnalysis/Zscripts/splitfilesbygenotypecomma_setupfiles_bothlsmandczi_updatedJAC.py " + location + "/warpingsmoothed/onlysmoothedtiffs")

#run split genotypes
os.system("python splitgenotypes_doubleoption_addvalue_updated")

#edit genotyping file so that all groups are included in final analysis
genotyping_file = open("genotyping", "r")
new_genotyping_file = open("new_genotyping", "w")

#run through lines of genotyping, add an asterisk in  front of comparison lines, and write to new_genotyping
#skip first line
line_counter = 1
for line in  genotyping.readlines():
	if line_counter == 1:
		line_counter = line_counter + 1
		new_genotyping_file.write(line)
		continue
	#take line and  put an  asterisk at the front, write to new_genotyping_file
	new_genotyping_file.write("*" + line)

genotyping_file.close()
new_genotyping_file.close()

#overwrite genotyping with contents of new_genotyping
os.system("mv new_genotyping genotyping")

#run splitfiles
os.system("python splitfilesbygenotypecomma_setupfiles_bothlsmandczi_updatedJAC.py")

#should now have jobsubmission.sh
#we won't run it directly, because we can run  it faster
#we will submit each job in the file, and read the out file to know when we can submit the next file
job_file =  open("jobsubmission.sh", "r")

for line in job_file.readlines():
	#only work with sbatch lines
	if line.startswith("sbatch"):
		#strip the newline off the line
		line_string = line.strip("\n")

		#add to string to allow for storing the job id
		line_string = line_string + " > analysis_job_info.txt"

		#submit the job and track the job id
		os.system(line_string)

		analysis_job_id_file = open("analysis_job_info.txt", "r")
		analysis_job_id = ""
		for line in analysis_job_id_file.readlines():
			analysis_job_id = line.split()[3].strip("\n")
		analysis_job_id_file.close()

		#track the outfile until the job starts analyzing (allowing for parallel  work, jobs die if they try to run in parallel  if they start at the same time)
		job_going = False
		while job_going == False:
			#check if string "Analyzing and transferring" is in the out file and only quit the loop  if it is (we are good to move one at this point)
			os.system("grep \"Analyzing and transferring\" host*" + str(analysis_job_id) + "*.out > analysis_grep.txt")

			#read analysis_grep.txt and see if the line is present, if so we can end the loop
			grep_a = open("analysis_grep.txt", "r")
			for line in grep_a.readlines():
				if "Analyzing and transferring" in line:
					job_going = True
			grep_a.close()

job_file.close()
#all analysis jobs have been pushed now


#delete hostname files
os.system("rm host*")
