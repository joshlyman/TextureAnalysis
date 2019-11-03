import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK



dir = '/Users/yanzhexu/Dropbox/EOR_ML_PI_Shared Regridded_Data/'
selectSlicefile = '/Users/yanzhexu/Desktop/Research/EOR_Andrea/EOR_PI_featuresMap_from_Andrea/EOR_Selected_Slice.csv'
checkslicewindowsDir = '/Users/yanzhexu/Desktop/Research/EOR_Andrea/EOR_PI_featuresMap_from_Andrea/checkSliceWindows/'


def getcaseslice(file):

    casedict = dict()
    with open(file, 'r') as csvinput:
        titlelist = csv.DictReader(csvinput, dialect='excel')
        for casetitle in titlelist:
            for casename in casetitle:
                if casename not in casedict:
                    casedict[casename]=list()
                    if casetitle[casename]!='':
                        casedict[casename].append(casetitle[casename])
                else:
                    if casetitle[casename]!='':
                        casedict[casename].append(casetitle[casename])
    return casedict


def getSlicepts(Tfile,T,sliceNum):

    Tmat = sio.loadmat(Tfile)

    if T == 'T1':
        Tarray = Tmat['T1Gd']
    else:
        Tarray = Tmat['T2']

    Tdim = np.shape(Tarray)

    ylistdim = Tdim[0]
    xlistdim = Tdim[1]

    # ROIlist = list()
    xlist = list()
    ylist = list()
    xylist = list()

    for xi in range(xlistdim):
        for yi in range(ylistdim):

        # in matlab, coordinate is larger than python for 1 pixel, they give slicenum, we define the x and y,
        # T2array starts from 0 after being imported
            ROIvalue = Tarray[yi,xi,sliceNum-1]

            if ROIvalue !=0:
                ylist.append(yi+1)
                xlist.append(xi+1)

                xylist.append(list())
                xylist[len(xylist)-1].append(xi+1)
                xylist[len(xylist)-1].append(yi+1)
                # ROIlist.append(ROIvalue)

    return xlist,ylist,xylist


def combineT1T2list(T1ROIxylist,T2ROIxylist):

    #1 means in T1, 0 means in T2
    T1T2ROIxylist = list()

    for xypair in T2ROIxylist:
        if xypair in T1ROIxylist:
            xypair.append(1)
            T1T2ROIxylist.append(xypair)
        else:
            xypair.append(0)
            T1T2ROIxylist.append(xypair)

    for xypair in T1ROIxylist:
        if xypair not in T2ROIxylist:
            xypair.append(1)
            T1T2ROIxylist.append(xypair)

    return T1T2ROIxylist


casedict = getcaseslice(selectSlicefile)

for case in casedict:
    slicelist = casedict[case]
    caseDir = os.path.join(dir, case)
    T1ROIDir = os.path.join(caseDir,'T1Gd.mat')
    T2ROIDir = os.path.join(caseDir,'T2fill.mat')

    print case

    for slice in slicelist:

        print "slice:",slice

        T1ROIxlist, T1ROIylist,T1ROIxylist = getSlicepts(T1ROIDir,'T1',int(slice))
        T2ROIxlist, T2ROIylist,T2ROIxylist = getSlicepts(T2ROIDir,'T2',int(slice))

        print 'T1 ROI list:',T1ROIxylist
        print len(T1ROIxylist)

        print 'T2 ROI list:',T2ROIxylist
        print len(T2ROIxylist)

        T1T2ROIxylist = combineT1T2list(T1ROIxylist,T2ROIxylist)
        print 'combine T1 T2 list:',T1T2ROIxylist
        print len(T1T2ROIxylist)

        # plt.plot(T2ROIxlist, T2ROIylist, 'g+')
        # plt.plot(T1ROIxlist, T1ROIylist, 'r+')
        #
        # plt.title(case + ' slice ' + slice + ' T1 and T2 ROI')
        # plt.savefig(checkslicewindowsDir + case + ' slice ' + slice + ' T1 and T2 ROI.png')
        # plt.cla()
        # plt.close()






