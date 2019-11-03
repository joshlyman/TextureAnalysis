import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET
import re


path ='/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Prediction'

outpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/NearBoundaryWindows'

# filename = 'CE_slice22_T2_ROI_Texture_Map_PredictY6.csv'
# filepath = os.path.join(path,filename)



for file in os.listdir(path):
    if not fnmatch.fnmatch(file,'*.csv'):
        continue

    print file

    slice = file.split('_')[0]
    slicenum = file.split('_')[1].split('slice')[1]

    filepath = os.path.join(path,file)

    with open(filepath,'r') as filecsv:
        filecsv.readline()

        rowFile = csv.reader(filecsv, delimiter=',')

        i = 0
        jumpx = list()
        jumpy = list()
        # jumpboundary = list()
        jumpcoord = list()

        outputfile = outpath + '/' + slice + ' ' + slicenum + '.csv'

        lastx = 0
        lasty = 0
        lastboundary = 0

        for row in rowFile:

            if i ==0:
                lastx = int(row[0])
                lasty = int(row[1])
                lastboundary = int(row[2])
            # else:
            #     lastrow = rowFile[i-1]
            #     lastx = int(row[0])
            #     lasty = int(row[1])
            #     lastboundary = int(row[2])

            i+=1
            curx = int(row[0])
            cury = int(row[1])
            Boundary = int(row[2])


            # if i!=0:
            if Boundary!=lastboundary:
                if lastboundary ==1 and Boundary ==0:
                    jumpx.append(curx)
                    jumpy.append(cury)
                    jumpcoord.append([curx,cury])
                    # jumpboundary.append('1')
                elif lastboundary ==0 and Boundary ==1:
                    jumpx.append(lastx)
                    jumpy.append(lasty)
                    jumpcoord.append([lastx, lasty])
                        # jumpboundary.append('1')

            lastx = curx
            lasty = cury
            lastboundary  = Boundary


    newfilename = outpath + '/' + slice + 'slice '+ slicenum+'.csv'
    featuretitle = ['X','Y','Boundary (1) or not (inside: 0) (outside:2)','Inside Boundary (1)or not(0)']

    with open(filepath,'r') as csvinput:
        with open(newfilename, 'wb') as csvoutput:
            csvwriter = csv.writer(csvoutput,dialect='excel')

            InterBoundary = 0
            for row in csv.reader(csvinput):
                if row[0] == 'X':
                    csvwriter.writerow(featuretitle)
                else:
                    newrowlist = list()
                    curx = int(row[0])
                    cury = int(row[1])
                    Boundary = int(row[2])

                    if [curx, cury] in jumpcoord:
                        InterBoundary = '1'
                    else:
                        InterBoundary ='0'

                    newrowlist.append(curx)
                    newrowlist.append(cury)
                    newrowlist.append(Boundary)
                    newrowlist.append(InterBoundary)
                    csvwriter.writerow(newrowlist)







