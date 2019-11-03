import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch

PIpath = '/Users/yanzhexu/Dropbox/EOR_ML_PI_Shared Regridded_Data/AR3530/AR3530_fromT2.mat'

Tmat = sio.loadmat(PIpath)

Tarray = Tmat['u']

# Tdim = np.shape(Tarray)


PIvalue = Tarray[156,72,70]

print PIvalue