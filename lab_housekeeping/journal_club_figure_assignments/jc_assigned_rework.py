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

#make a copy of lab_members to not be copied
lab_members_copy = lab_members

#create a dictionary to hold lab members and assigned figure
assignments = {}

#randrange(fig_num) + 1

#handle assignments, based on number of lab members and number of figures
if len(lab_members) == fig_num:
        #same
        #assign 1 figure to 1 member
        for i in range(len(lab_members_copy)):
                #pick an index of lab_members to be assigned figure i
                #base range on length of lab_members, which shrinks on each pass
                index = randrange(len(lab_members))
                member = lab_members[index]
                assignments[member] = i + 1

                #print(lab_members,lab_members_copy)
                del lab_members[index]     

elif len(lab_members) > fig_num:
        #more members
        #assign 1 figure to 1 member, assign "None!" to anyone who does not get one
        for i in range(fig_num):
                #pick an index of lab_members to be assigned figure i
                #base range on length of lab_members, which shrinks on each pass
                index = randrange(len(lab_members))
                member = lab_members[index]
                assignments[member] = i + 1

                #print(lab_members,lab_members_copy)
                del lab_members[index]

        #for each remaining lab member, assign "None!"
        for i in range(len(lab_members)):
                assignments[lab_members[i]] = "None!"
elif len(lab_members) < fig_num:
        #more figures
        #assign consecutive figures to lab members to exhaust figure count
        #print("hi")

        #break up figures into groups (equal to # lab members) to be assigned to each member
        #adjacent numbers of figures to be assigned (i.e. 1+2, 3+4, etc.)

        #max number of figures per member, rounded up
        #i.e. if 6 figures and 4 members, 2 members get 2 and 2 get 1
        #i.e. if 9 figures and 4 members, 1 member gets 3 and 3 get 2
        max_num_figures_per_member = int(fig_num/len(lab_members)) + 1
        #print(max_num_figures_per_member)
        min_num_figures_per_member = max_num_figures_per_member - 1
        #print(min_num_figures_per_member)

        #create assignment groups
        #groups should equal the number of members
        max_fig_mem_count = fig_num - (min_num_figures_per_member * len(lab_members))
        #print(max_fig_mem_count)
        min_fig_mem_count = int((fig_num - (max_fig_mem_count * max_num_figures_per_member)) / min_num_figures_per_member)
        #print(min_fig_mem_count)

        total_num_groups = max_fig_mem_count + min_fig_mem_count

        #assign figure numbers to each group
        groups = []

        fig_num_tracker = 1

        for i in range(total_num_groups):
                #assign min or max number of figures to group, based on value of i
                #if i is less than max_fig_mem_count, apply the max; otherwise apply the min
                if i < max_fig_mem_count:
                        group = []
                        for j in range(max_num_figures_per_member):
                                #append fig_num_tracker and then add 1
                                group.append(fig_num_tracker)
                                fig_num_tracker = fig_num_tracker + 1
                        #append group to groups
                        groups.append(group)
                else:
                        group = []
                        for j in range(min_num_figures_per_member):
                                #append fig_num_tracker and then add 1
                                group.append(fig_num_tracker)
                                fig_num_tracker = fig_num_tracker + 1
                        #append group to groups
                        groups.append(group)

        #now assign each group in groups to a member
        for i in range(len(groups)):
                #pick an index of lab_members to be assigned groups[i]
                #base range on length of lab_members, which shrinks on each pass
                index = randrange(len(lab_members))
                member = lab_members[index]
                assignments[member] = groups[i]

                #print(lab_members,lab_members_copy)
                del lab_members[index]   

for lab_mem in assignments:
        print(lab_mem + ": " + str(assignments[lab_mem]))

