#!/usr/bin/env python

#Ari Ginsparg
#11/19/19
#The purpose of this program is to generate a consensus sequence from an aligned and normalized fasta file
#Sequences must all be of the same length for this program to work properly
#The sequence is outputted as raw text
#program takes in the requested fasta file, as well as a cutoff for where to determine whether to mark a consensus at a given locus, or mark as variable
#cutoff is to be entered as a decimal below 1, with 1 requiring full consensus
#variable loci will be marked with an X

import sys
import os

#extract arguments
my_args = sys.argv
file_name = my_args[1]
cutoff = my_args[2]
#cast cutoff to a float
cutoff = float(cutoff)

#open the fasta file
myFile = open(file_name, "r+")

#create list to hold all sequences
sequences = []

for line in myFile:
	#add line to sequences
	if(line[0] != ">"):
		sequences.append(line)

#variable to hold the built consensus sequence
consensus = ""

#look through the sequences list to generate the consensus, locus by locus
#outer loop iterates across the length of the sequences
for locus in range(len(sequences[0])):

	#create empty list to hold all the amino acids/nucleotides at the locus, as well as count the frequency of the values
	consensus_list = []

	#Add values to the consensus list at the given locus
	for sequence in sequences:
		
		#variable to indicate whether the variable has been found or not
		value_found = False

		#run through the consensus list to determine if sequence[locus] already exists
		#append new value to list if it does not, increase value for the counter
		for value in range(len(consensus_list)):
			if(consensus_list[value][0] == sequence[locus]):
				consensus_list[value][1] = consensus_list[value][1] + 1

				value_found = True

		#append new value if not found with initial count of 1
		if (value_found == False):
			consensus_list.append([sequence[locus], 1])

	#determine what the consensus value is
	#if majority is not at least the cutoff, value at locus will be an X

	#value to hold highest count
	highest_count = 0
	#variable to hold the value that corresponds with the highest count
	highest_count_value = "X"

	#loop to go through and determine the most prevalent value from the consensus_list
	for value in consensus_list:
		if(value[1] > highest_count):
			highest_count = value[1]
			highest_count_value = value[0]

	#determine whether to add highest_count_value, if its prevalence exceeds or is equal to the cutoff
	if(highest_count >= (len(sequences) * cutoff)):
		consensus += highest_count_value
	else:
		consensus += "X"

print(consensus)
