import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK

imgpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/Hu Data Tumor Masks_V3/RWh_HU0007/HU0007T2fill_MP_T2mask.mat'

#imgpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/Hu Data Tumor Masks_V3/RWh_HU0007/T2/T2.mat'

rootDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Prediction'


predictionfile = 'RW_slice20_T2_ROI_Texture_Map_PredictY6.csv'

slicenum = 17


# get predict value from prediction file
def generatexyp(predictionfile):
    predfile = os.path.join(rootDir,predictionfile)

    with open(predfile, 'r') as predictFile:
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')

        xlist = list()
        ylist = list()
        for row in rowFile:
            xlist.append(int(row[0]))
            ylist.append(int(row[1]))

    return xlist,ylist


def generatePlist(xlist,ylist,file,slicenum):
    # ptsfolder = ptsdict[newpatientname]
    # T2matfile = os.path.join(imgpath, ptsfolder)
    T2matfile = file
    T2mat = sio.loadmat(T2matfile)
    T2array = T2mat['u']

    plist = list()
    for i in range(len(xlist)):
        x = xlist[i]
        y = ylist[i]
        pvalue = T2array[y,x,slicenum]
        plist.append(pvalue)

    return plist


xlist,ylist = generatexyp(predictionfile)

# get plist from Hu data dict
plist = generatePlist(xlist,ylist,imgpath,int(slicenum))


print xlist
print ylist
print plist