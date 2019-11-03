import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK




rcbvpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/GBM_SlidingWindow_TextureMap/CE_slice22_T2_ROI_Texture_Map.csv'

with open(rcbvpath, 'r') as tfile:
    tfile.readline()
    rowFile = csv.reader(tfile, delimiter=',')

    rcbvlist = dict()

    i = 0
    for row in rowFile:
        if row[0] == 'RCBV':
            i+=1

            xn = int(row[2])
            yn = int(row[3])
            rcrawmean = float((row[42]))

            xyc = str(xn) + '_' + str(yn)

            rcbvlist[xyc] = rcrawmean








