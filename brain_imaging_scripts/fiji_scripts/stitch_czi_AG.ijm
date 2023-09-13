source_dir = getDirectory("Source Directory");
//target_dir = getDirectory("Target Directory");


list = getFileList(source_dir);
list = Array.sort(list);
for (i=0; i<list.length; i++) {

	//get name and open
  	ImageName = source_dir + list[i];
	//run("Bio-Formats Importer", "open='"+ ImageName +"' color_mode=Default view=Hyperstack stack_order=XYCZT open_files_individually series_1");
	run("Bio-Formats Windowless Importer", "open=" + ImageName);
	// split channels
	run("Split Channels");

	//convert channel 1 to nrrd
	split_channel_1 = "C1-" + list[i] + " - " + list[i] + " #1";
	//select
	selectWindow(split_channel_1);
	//rename to conform better to downstream pipeline standards
	//get upstream of period
	split_up_name = split(list[i], ".");
	split_up_name_parentheses = split(list[i], "(");
	split_up_name_no_num = split_up_name_parentheses[0];
	split_up_name_num = split(split_up_name_parentheses[1], ")");
	full_name = split_up_name_no_num + "_" + split_up_name_num[0];
	//split further to extract around parentheses (file number contained in parentheses)
	//want file number between underscores
	rename(full_name + "_02");
	output_image_1 = source_dir + full_name + "_02";
	run("Nrrd ... ", "nrrd=[" + output_image_1 + ".nrrd]");
	close();

	//convert channel 2 to nrrd
	split_channel_1 = "C2-" + list[i] + " - " + list[i] + " #1";
	selectWindow(split_channel_1);
	//rename to conform better to downstream pipeline standards
	//get upstream of period
	//split_up_name = split(list[i], ".");
	rename(full_name + "_01");
	output_image_1 = source_dir + full_name + "_01";
	run("Nrrd ... ", "nrrd=[" + output_image_1 + ".nrrd]");
	close();

	//close both
	
}
