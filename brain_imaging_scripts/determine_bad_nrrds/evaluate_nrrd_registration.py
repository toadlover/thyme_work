import os,sys, argparse
import numpy as np
import nrrd
import math

#input args: registration file (index 1) and 
#default registration = /data/project/thymelab/sthyme/stuffonboxbutdonotdelete/imagingscripts/registration/Ref20131120pt14pl2flip.nrrd
#declare argparse arguments
parser = argparse.ArgumentParser()
parser.add_argument("directory", type=str, help = "Directory that the imaging data is in. Should be full path string (derived from pwd)")
parser.add_argument("-i", type=str, help = "Image used in registration.", default = "/data/project/thymelab/sthyme/stuffonboxbutdonotdelete/imagingscripts/registration/Ref20131120pt14pl2flip.nrrd")

#parse args
args = parser.parse_args()

registration_image_name = args.i

location = args.directory

#read the registration file
readdata, header = nrrd.read(registration_image_name, index_order='C')
print(readdata.shape)
print(header)


#make an nrrd of registration that flattens the image about the z axis and takes a sum of intensities across all layers

flattened_array = np.ndarray(shape=(readdata.shape[1],readdata.shape[2]),dtype=float)

for stack in range(readdata.shape[0]):
	#print(stack)

	flattened_array = flattened_array + readdata[stack]

#test output of flattened registration
nrrd.write("flattened_registration.nrrd", flattened_array)

largest = 0
largest_coords = [0,0]

#find the highest sum value in the stack
for x in range(flattened_array.shape[0]):
	for y in range(flattened_array.shape[1]):
		if flattened_array[x,y] > largest:
			largest = flattened_array[x,y]
			largest_coords = [x,y]

print(largest, largest_coords)

#make new version on flattened_registration that defines pixels as bright or not
#to be considered bright, sum value must be at least 40% of the max

#identify the boundaries of the occupied region for the y coordinates
#will use these to help narrow down the area investigated on registered images
#primarily, this is to rule out images with extremely bright staining on the eyes that is far greater than that on the brain (which throws off a small but significant portion of images)
y_bound_min = -1
y_bound_max = -1

flattened_array_simplified = np.ndarray(shape=(readdata.shape[1],readdata.shape[2]),dtype=float)
for x in range(flattened_array.shape[0]):
	for y in range(flattened_array.shape[1]):
		if flattened_array[x,y] > largest * 0.7:
			flattened_array_simplified[x,y] = largest
			#set y_bound_min and y_bound_max initially on the first bright pixel encountered
			if y_bound_min == -1:
				y_bound_min = y
			if y_bound_max == -1:
				y_bound_max = y
			#set y min and max if encountering a y higher or lower
			if y > y_bound_max:
				y_bound_max = y
			if y < y_bound_min:
				y_bound_min = y
		else:
			flattened_array_simplified[x,y] = 0

print(y_bound_min,y_bound_max)

#print simplified
nrrd.write("flattened_registration_simplified.nrrd", flattened_array_simplified)

#run this process for all nrrds in the directory
#need to flatten and simplify the nrrd
#then compare areas of current nrrd against registration

#lists to hold good and bad registrations
good_registrations = []
bad_registrations = []

for r,d,f in os.walk(location):
	for file in f:
		#we have a file to work with
		if file.endswith(".nrrd") and "flattened" not in file and location == r:
			readdata2, header2 = nrrd.read(r + "/" + file, index_order='C')

			print(r + "/" + file)
			print(readdata2.shape)
			print(header2)


			#for stack in range(readdata2.shape[0]):
			#	for x in range(readdata2.shape[1]):
			#		for y in range(readdata2.shape[2]):
			#			print(readdata2[stack][x][y])

			#write_file = open(r + "/contents_" + file + ".txt", "w")
			#write_file.write(str(readdata))
			#write_file.close()

			nrrd.write(r + "/unflattened_" + file, readdata2)

			flattened_array2 = np.ndarray(shape=(readdata2.shape[1],readdata2.shape[2]),dtype=float)

			flattened_array2.fill(0)

			
			for stack in range(readdata2.shape[0]):
				print(stack)

				#run through stack and see if any values are not numbers (this may be an issue)
				#if any are not numbers, set value to 0
				for x in range(readdata2.shape[1]):
					for y in range(readdata2.shape[2]):
						#ignore if not within the y boundaries
						if y < y_bound_min or y > y_bound_max:
							continue


						#print(stack,x,y)
						if math.isinf(readdata2[stack][x][y]):
							readdata2[stack][x][y] = 1000000
							print("is infinity at " + str([stack,x,y]))
						if math.isnan(readdata2[stack][x][y]):
							readdata2[stack][x][y] = 0
							print("is nan at " + str([stack,x,y]))

						flattened_array2[x,y] = flattened_array2[x,y] + readdata2[stack][x][y]

			#test output of flattened registration
			nrrd.write(r + "/flattened_" + file, flattened_array2)
			
			largest = 0
			largest_coords = [0,0]

			#find the highest sum value in the stack
			for x in range(flattened_array2.shape[0]):
				for y in range(flattened_array2.shape[1]):

					if flattened_array2[x,y] > largest:
						largest = flattened_array2[x,y]
						largest_coords = [x,y]

			print(largest, largest_coords)

			#make new version on flattened_registration that defines pixels as bright or not
			#to be considered bright, sum value must be at least 40% of the max


			flattened_array_simplified2 = np.ndarray(shape=(readdata2.shape[1],readdata2.shape[2]),dtype=float)
			for x in range(flattened_array2.shape[0]):
				for y in range(flattened_array2.shape[1]):
					if flattened_array2[x,y] > largest * 0.7:
						flattened_array_simplified2[x,y] = largest
					else:
						flattened_array_simplified2[x,y] = 0

			#print simplified
			nrrd.write(r + "/flattened_simplified_" + file, flattened_array_simplified2)
			

			#now go and compare registered image (iterated in loop) against registration
			#run through all pixels in each simplified image
			#this assumes the registration image and registered images are the same size (I think they have to be?)
			total_pixels = flattened_array.shape[0] * flattened_array.shape[1]

			#counters for bright pixels as well as overlap betwen registration and registered
			registered_bright_pixels = 0
			registration_bright_pixels = 0
			overlapped_pixels = 0

			for x in range(flattened_array2.shape[0]):
				for y in range(flattened_array2.shape[1]):
					
					#registration
					if flattened_array_simplified[x][y] != 0:
						registration_bright_pixels = registration_bright_pixels + 1

					#registered
					if flattened_array_simplified2[x][y] != 0:
						registered_bright_pixels = registered_bright_pixels + 1


					#overlap
					if flattened_array_simplified[x][y] != 0 and flattened_array_simplified2[x][y] != 0:
						overlapped_pixels = overlapped_pixels + 1

			print("total_pixels, registration_bright_pixels, registered_bright_pixels, overlapped_pixels")
			print(total_pixels, registration_bright_pixels, registered_bright_pixels, overlapped_pixels)

			overlap_to_registration_total = float(overlapped_pixels / registration_bright_pixels)
			
			#handling in case we have no bright pixels in the registered image (which is reasonable to see in bad registrations)
			overlap_to_registered_total = 0

			if registration_bright_pixels > 0:
				overlap_to_registered_total = float(overlapped_pixels / registered_bright_pixels)

			#get the well id
			well_id = file.split("_")[len(file.split("_")) - 4]

			#if at least 50% overlap, it is probably good
			if overlap_to_registration_total > 0.4 or overlap_to_registered_total > 0.4:
				good_registrations.append(well_id)
			else:
				bad_registrations.append(well_id)

print("Good registrations: ", good_registrations)
print("Bad registrations: ", bad_registrations)

good_reg_file = open("good_registrations.txt", "w")
bad_reg_file = open("bad_registrations.txt", "w")

for reg in good_registrations:
	good_reg_file.write(str(reg) + ",")

for reg in bad_registrations:
	bad_reg_file.write(str(reg) + ",")
