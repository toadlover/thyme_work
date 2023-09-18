import os, sys
for i in os.listdir("."):
    if os.path.isdir(i) & (i != "job_out"):
        os.chdir(i)
        os.system('''csplit --suffix-format="%04d.sdf" --suppress-matche -f ''' + i + ''' -z split '/$$$$/' {*}''')
        os.chdir("..")


