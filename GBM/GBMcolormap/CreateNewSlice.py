import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET
import re


predfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/CE22_0413/NewEGFR.csv'

outputMapDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/CE22_0413/'

outputfile = 'NewEGFR2.csv'

with open(predfile, 'r') as predictFile:
    rowFile = csv.reader(predictFile, delimiter=',')

    i = 0
    xlist = list()
    ylist = list()
    plist = list()
    for row in rowFile:
        i += 1
        x = int(row[0])
        y = int(row[1])
        p = float(row[2])

        for xi in range(x-4,x+4):
            for yi in range(y-4,y+4):
                pi = p

                xlist.append(xi)
                ylist.append(yi)
                plist.append(pi)

outputpath = outputMapDir + outputfile

with open(outputpath, 'wb') as csvoutput:
    csvwriter = csv.writer(csvoutput, dialect='excel')

    i = 0

    for ei in range(len(xlist)):
        newx = xlist[ei]
        newy = ylist[ei]
        newp = plist[ei]

        row = [str(newx),str(newy),str(newp)]
        csvwriter.writerow(row)

        i+=1

    print i


