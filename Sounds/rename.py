import os
exit(0)
## This was once used to rename sound files. I'll leave it here in case anyone needs it.
#
#path = "."
#
#i = 0
#filepaths = []
#for (path, dirs, files) in os.walk(path):
#    print path
#    print dirs
#    print files
#    for file in files:
#        if os.path.isfile(file):
#            if file.endswith('wav'):
#                filepaths.append(file)#
#
## Re-populate list with filename, size tuples
#for i in xrange(len(filepaths)):
#    filepaths[i] = (filepaths[i], os.path.getsize(filepaths[i]))
#
#filepaths.sort(key=lambda filename: filename[1], reverse=False)
#
##for file in filepaths:
#for i in xrange(len(filepaths)):
#    newfile= "beep_{num:03d}.wav".format(num=i+1)
#    print filepaths[i][0]+" " + str(filepaths[i][1]) +" " +newfile
#    os.rename(filepaths[i][0], newfile)