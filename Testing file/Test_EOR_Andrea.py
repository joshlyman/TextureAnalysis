import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK


# dir = '/Users/yanzhexu/Dropbox/EOR_ML_PI_Shared Regridded_Data/'



T1file = '/Users/yanzhexu/Dropbox/EOR_ML_PI_Shared Regridded_Data/AR3530/AR3530_fromT1Gd.mat'

T2file = '/Users/yanzhexu/Dropbox/EOR_ML_PI_Shared Regridded_Data/AR3530/AR3530_fromT2.mat'


# 'T1Gd'
T1mat = sio.loadmat(T1file)

# 'T2'
T2mat = sio.loadmat(T2file)


T1array = T1mat['u']
T2array = T2mat['u']

T2dim = np.shape(T2array)

# For AR3530: (215,215,156)
ylistdim = T2dim[0]
xlistdim = T2dim[1]
ttslicenum = T2dim[2]



# print ttslicenum
slicenum = 70

# if define range(slicenum), then do not need to use slicenum - 1

plist = list()
xlist = list()
ylist = list()

p1list = list()
x1list = list()
y1list = list()



# for xi in range(xlistdim):
#     for yi in range(ylistdim):
#
#     # in matlab, coordinate is larger than python for 1 pixel, they give slicenum, we define the x and y,
#     # T2array starts from 0 after being imported
#
#         pvalue = T1array[yi,xi,slicenum-1]
#
#         if pvalue !=0:
#             y1list.append(yi)
#             x1list.append(xi)
#             p1list.append(pvalue)


for xi in range(xlistdim):
    for yi in range(ylistdim):

    # in matlab, coordinate is larger than python for 1 pixel, they give slicenum, we define the x and y,
    # T2array starts from 0 after being imported

        pvalue = T2array[yi,xi,slicenum-1]

        if pvalue !=0:
            ylist.append(yi)
            xlist.append(xi)
            plist.append(pvalue)

# plt.figure(figsize=(18, 13))
plt.figure()

cm = plt.cm.get_cmap('jet')

plt.scatter(xlist, ylist, c=plist, vmin=0, vmax=1, cmap=cm)

#
# cm1 = plt.cm.get_cmap('Greys')
# plt.scatter(x1list, y1list, c=p1list, vmin=0, vmax=1, cmap=cm1)


plt.colorbar()

print plist
# plt.show()
