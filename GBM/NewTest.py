import os
import fnmatch
import matplotlib.pyplot as plt
import csv

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/T1 and T2 texture Maps - grid spacing 4'


wholexlist = list()
wholeylist = list()

for texturemapfile in os.listdir(rootDir):

    if texturemapfile.startswith('.'):
        continue
    if texturemapfile.startswith('..'):
        continue

    print texturemapfile

    patientname = texturemapfile.split('_')[0]
    if fnmatch.fnmatch(patientname,"*FSL*"):
        newpatientname = patientname.replace("FSL","")
    elif fnmatch.fnmatch(patientname,"*h*"):
        newpatientname = patientname.replace("h","")
    else:
        newpatientname = patientname
    print newpatientname


    slicenum = texturemapfile.split('_')[1].replace('slice','')
    slicenum = int(slicenum)
    print slicenum

    TROI = texturemapfile.split('_')[2]
    print TROI


    # start to get file and draw

    plt.figure()
    mincontourlist = list()
    maxcontourlist = list()

    xydict = dict()
    xcoordlist = list()
    ycoordlist = list()

    texturefile = os.path.join(rootDir,texturemapfile)
    with open(texturefile, 'r') as roiFile:
        for i in range(9):
            roiFile.readline()

        rowFile = csv.reader(roiFile, delimiter=',')
        for row in rowFile:

            # only study one contrast since others are same
            if row[0]!= 'EPI+C':
                continue

            # get y coordinate
            ycoord = int(float(row[2]))
            ycoordlist.append(ycoord)
            wholeylist.append(ycoord)
            print ycoord

            # get x coordinate
            xcoord = int(float(row[3]))
            xcoordlist.append(xcoord)
            wholexlist.append(xcoord)
            print xcoord

wholeminx = min(wholexlist)
wholemaxx = max(wholexlist)
wholeminy = min(wholeylist)
wholemaxy = max(wholeylist)

print 'x: min,max',wholeminx,wholemaxx
print 'y: min,max',wholeminy,wholemaxy