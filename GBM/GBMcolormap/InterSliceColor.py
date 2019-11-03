import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET
import re

predfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/CE22_0413/tumorContent_slice22_PDGFRA_alpha45000.csv'

outputMapDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/CE22_0413/'

outputfile = 'NewPDGFRA.csv'

def generatexyp(predictionfile):
    predfile = predictionfile

    i = 0
    with open(predfile, 'r') as predictFile:

        rowFile = csv.reader(predictFile, delimiter=',')

        xlist = list()
        ylist = list()
        plist = list()
        for row in rowFile:
            i+=1
            xlist.append(int(row[0]))
            ylist.append(int(row[1]))
            plist.append(float(row[2]))


    # print i
    return xlist,ylist,plist


xlist, ylist, plist = generatexyp(predfile)


newxlist = list()
newylist = list()
newplist = list()


for i in range(len(ylist)):
    cx = xlist[i]
    cy = ylist[i]
    cp = plist[i]

    if i == len(ylist)-1:
        newxlist.append(cx)
        newylist.append(cy)
        newplist.append(cp)
    else:
        ax = xlist[i+1]
        ay = ylist[i + 1]
        ap = plist[i+1]

        # print 'why1'

        if cy !=ay:
            # print 'why2'

            newxlist.append(cx)
            newylist.append(cy)
            newplist.append(cp)
        else:
            # print 'why3'
            newxlist.append(cx)
            newylist.append(cy)
            newplist.append(cp)

            if ap > cp:
                # print 'why4'
                diff = ap - cp
                nop = ax - cx
                intediff = diff/nop

                for ii in range(nop-1):
                    interx = cx + (ii + 1)
                    interp = cp + (ii + 1)*intediff
                    intery = cy

                    # print interx
                    # print interp
                    # print intery

                    newxlist.append(interx)
                    newylist.append(intery)
                    newplist.append(interp)
            else:
                # print 'why5'
                diff = cp - ap
                nop = ax - cx
                intediff = diff / nop

                for ii in range(nop-1):
                    interx = cx + (ii + 1)
                    interp = cp - (ii + 1) * intediff
                    intery = cy

                    # print interx
                    # print interp
                    # print intery


                    newxlist.append(interx)
                    newylist.append(intery)
                    newplist.append(interp)



# print newxlist
# print newylist
# print newplist

outputpath = outputMapDir + outputfile

with open(outputpath, 'wb') as csvoutput:
    csvwriter = csv.writer(csvoutput, dialect='excel')

    i = 0

    for ei in range(len(newxlist)):
        newx = newxlist[ei]
        newy = newylist[ei]
        newp = newplist[ei]

        row = [str(newx),str(newy),str(newp)]
        csvwriter.writerow(row)

        i+=1

    print i