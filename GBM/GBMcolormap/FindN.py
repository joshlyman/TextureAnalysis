import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK


# Necrosis value list
NecrosDir='/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/GBMNecurfiles/NecrosisValue'


for file in os.listdir(NecrosDir):
    if file.startswith('.'):
        continue
    if file.startswith('..'):
        continue
    if fnmatch.fnmatch(file,'*Icon*'):
        continue
    if file != 'CE slice22Necur.csv':
        continue

    filepath = os.path.join(NecrosDir,file)

    with open(filepath, 'r') as Nfile:
        Nfile.readline()
        rowFile = csv.reader(Nfile, delimiter=',')

        NE = list()
        # xN = list()
        # yN = list()

        for row in rowFile:
            if row[0] =='':
                continue

            xn = int(row[0])
            yn = int(row[1])
            ne = int(row[5])

            if ne == 1:
                N = list()
                NE.append(N)
                N.append(xn)
                N.append(yn)


    print NE

