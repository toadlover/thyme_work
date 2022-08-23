#!/usr/bin/env python

#Ari Ginsparg
#10/28/19
#The purpose of this program is to take in a fasta file (file name given in command line argument),
#and normalize the sequence lines by condensing the sequences into a single line for easier processing
#Program outputs via print function, can use additional command line functions to direct output

import sys

#extract arguments
my_args = sys.argv
file_name = my_args[1]

#open the fasta file
myFile = open(file_name, "r+")

#variable to hold the built sequence
sequence = ""

#process the file line by line
for line in myFile:

	#remove the last character of each line (which is a newline character)
	temp = line[:-1]

	#output line if it is the header statement
	if(len(temp) >= 1 and temp[0] == ">"):
		#print the built sequence (if one is built), then clear it after printing to build a new one
		if(sequence != ""):
			print(sequence)
			sequence = ""

		#print the header
		print(temp)
	#if line is part of a sequence, append to the sequence string
	if(len(temp) >= 1 and temp[0] != ">"):
		sequence += temp

#print the last sequence before ending the program
print(sequence)

