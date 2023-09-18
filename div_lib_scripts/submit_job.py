import os,sys

program = sys.argv[1]

print(program)

#remove submit.out
os.system("rm submit.out")
#touch to make fresh submit.out
os.system("touch submit.out")

#check through contents of submit.out. If no successful submit has occured, try to submit inputted program
while True:
	out_file = open("submit.out", "r")
	submitted = False
	for line in out_file.readlines():
		if "Submitted" in line:
			#we submitted the job
			submitted = True
			break
	if submitted == True:
		break

	out_file.close()

	#submit the job again
	os.system("sbatch " + program + " > submit.out")
