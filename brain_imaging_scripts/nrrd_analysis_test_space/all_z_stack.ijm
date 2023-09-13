source_dir = getDirectory("Source Directory");
//target_dir = getDirectory("Target Directory");


list = getFileList(source_dir);
list = Array.sort(list);
for (i=0; i<list.length; i++) {

	//get name and open
  	ImageName = source_dir + list[i];
	run("Bio-Formats Importer", "open='"+ ImageName +"' color_mode=Default view=Hyperstack stack_order=XYCZT open_files_individually series_1");

	//get number of file by splitting string
	split_up_name = split(ImageName, "_");
	rename(split_up_name[split_up_name.length - 4]);

	//project file
	run("Z Project...", "projection=[Sum Slices]");

	close(split_up_name[split_up_name.length - 4]);
}
