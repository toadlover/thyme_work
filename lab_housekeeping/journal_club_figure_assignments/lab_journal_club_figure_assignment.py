#script to read in a list of lab members for randomly assigning figures for a journal club paper
#first line is the number of figures to work with for the given paper
#following lines are the names of lab members

import os
from random import randrange

file = open("jc_members.txt", "r")

line_counter = 1

fig_num = 0
lab_members = []

for line in file.readlines():

        #take the number of figures
        if line_counter == 1:
                line_counter = line_counter + 1
                fig_num = int(line.split("\n")[0])
                continue

        #take in lab members
        lab_members.append(line.split("\n")[0])

#create a dictionary to hold lab members and assigned figure
assignments = {}

#if number of figures is less than or equal to the number of members
#assign a figure to each person (may have some duplicates)
if fig_num <= len(lab_members):

        all_covered = False

        #variable to limit the number of repeats (i.e. don't put 3 people on a figure unless we mathematically have to)
        #this will likely be 1
        #add 1 to the value for the max number of people to get the figure
        repeat_limit = int(len(lab_members) / fig_num)

        if repeat_limit == 1:
                repeat_limit = repeat_limit + 1

        for mem in lab_members:
                all_covered = len(assignments) >= fig_num

                #make sure no repeats until we have covered every figure, then move on to duplicates
                if all_covered == False:
                        assignments[mem] = randrange(fig_num) + 1

                        #check if already covered, and if so then reroll  until taking unoccupied
                        reroll = True
                        while reroll == True:
                                reroll = False

                                #reroll if necessary
                                if reroll == True:
                                        assignments[mem] = randrange(fig_num) + 1


                #when all covered, handle duplicates (should only happen if there are more members than figures)
                if all_covered == True:
                        assignments[mem] = randrange(fig_num) + 1

                        #check if figure is over-covered and if so, reassign mem
                        instance_count = 0
                        for x in assignments:
                                if assignments[x] == assignments[mem]:
                                        instance_count = instance_count + 1

                        #reroll until we fill out fairly
                        if instance_count > repeat_limit:
                                reroll = True
                                while reroll == True:
                                        reroll = False

                                        #check if figure is over-covered and if so, reassign mem
                                        instance_count = 0
                                        for x in assignments:
                                                if assignments[x] == assignments[mem]:
                                                        instance_count = instance_count + 1

                                        if instance_count > repeat_limit:
                                                reroll = True

                                        #reroll if necessary
                                        if reroll == True:
                                                assignments[mem] = randrange(fig_num) + 1
#handle if we have more figures than lab members
else:
        #create lists of figures grouped together(cluster adjacent figures together starting from the beginning)

        max_figs_per_mem = int(fig_num/len(lab_members))
        #ensure at least 2
        if max_figs_per_mem <= 1:
                max_figs_per_mem = 2

        #make list of lists
        master_list = []
        sub_list = []
        for i in range(1,fig_num + 1):
                sub_list.append(i)
                #list full, append to master and make new list
                if len(sub_list) == max_figs_per_mem:
                        master_list.append(sub_list)
                        sub_list = []

                if i == fig_num:
                        master_list.append(sub_list)
        #print(master_list)

        if len(master_list[len(master_list) - 1]) == 0:
                master_list.pop()

        #break up sub_lists at end until the length of master_list is equal to the number of lab members
        iterator = len(master_list) - 1

        if len(master_list[iterator]) == 1:
                iterator = iterator - 1

        while len(master_list) != len(lab_members):


                if len(master_list[iterator]) == 1:
                        continue

                new_list = []

                new_list.append(master_list[iterator].pop())
                master_list.append(new_list)
                iterator = iterator - 1


        #print(master_list, fig_num, len(lab_members), max_figs_per_mem)

        #randomly assign lists from master to members, no repitition
        for mem in lab_members:
                assignments[mem] = master_list[randrange(len(master_list))]

                #check if already covered, and if so then reroll  until taking unoccupied
                reroll = True
                while reroll == True:
                        reroll = False

                        for x in assignments:
                                if assignments[x] == assignments[mem] and x != mem:
                                        reroll = True

                        #reroll if necessary
                        if reroll == True:
                                assignments[mem] = master_list[randrange(len(master_list))]


#print(assignments)

for lab_mem in assignments:
        print(lab_mem + ": " + str(assignments[lab_mem]))

