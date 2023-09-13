#!/bin/bash
#Ari Ginsparg
#1/15/20
#The purpose of this script is to activate the conda environment that allows the behavior scripts to run, using the environment that is in the thymelab directory
#This script can be used by any user, regardless of experience
#When running the program, enter the yml file that you want to create/run the environment for
#Example ./environment_setup.sh environment.yml

echo "Welcome! Setting up behavior python environment script."

#Currently not working
#load Anaconda
#echo "Loading Anaconda"
#module load Anaconda3/5.3.1

#name of environment (defined in the input yml file)
#read the yml file line by line
while IFS= read -r line
do

	#check if the line contains "name: " to get environment name
	if [[ $line == "name: "* ]]
	then
		#remove first 6 characters from line and save remainder as name of environment
		name=${line:6}
	fi
done < "$1" 

#get name of user
user=$(whoami)
#define path to environment (based on default environment write path of conda)
path=/home/$user/.conda/envs/$name

echo "Checking if $name exists."

#Creates thymelab conda environment if it does not already exist, save to home directory (based on yml file)
if [[ ! -d $path ]]
then
    echo "Creating new $name environment."
    conda env create -f $1
    echo "========================================================"
    echo "Enter the following command to activate Anaconda3:"
    echo "module load Anaconda3/5.3.1"
    echo "========================================================"
else
	#Prompt user to activate the environment if it exists
	echo "$name environment exists."
	echo "========================================================"
	echo "Enter the following command to activate Anaconda3:"
    echo "module load Anaconda3/5.3.1"
    echo "========================================================"
	echo "Enter the following command to activate the environment:"
	echo "source activate $name"
	echo "========================================================"
fi



#Activate the environment
#Currently not working
#eval "$("source activate thymelab")"
