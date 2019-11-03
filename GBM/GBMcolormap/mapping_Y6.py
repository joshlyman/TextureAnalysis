import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET


rootDir = '/Users/yanzhexu/Dropbox/Prediction/'

predictiondict = dict()

for predictionfile in os.listdir(rootDir):

    if predictionfile.startswith('.'):
        continue
    if predictionfile.startswith('..'):
        continue
    if fnmatch.fnmatch(predictionfile,'*Icon*'):
        continue


    print predictionfile

    ptsname = predictionfile.split('_')[0]
    slicename = predictionfile.split('_')[1]
    slicenum = slicename.replace('slice','')

    predictiondict[ptsname+'_'+slicenum] = predictionfile


    # print ptsname
    # print slicenum



# print predictiondict
# print len(predictiondict)


