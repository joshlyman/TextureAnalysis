import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK


dir = '/Users/yanzhexu/Dropbox/EOR_ML_PI_Shared Regridded_Data/'

outDir = '/Users/yanzhexu/Desktop/Research/EOR_Andrea/EOR_PI_featuresMap_from_Andrea/T1ROIoverT1PI/'

def drawColorMap(T1file,T1PIfile, caseoutDir,casefolder):

    Tmat = sio.loadmat(T1file)
    TPImat = sio.loadmat(T1PIfile)

    # 0 or 1 inside
    TROIarray = Tmat['T1Gd']

    # PI inside
    TPIarray = TPImat['u']

    Tdim = np.shape(TROIarray)

    ylistdim = Tdim[0]
    xlistdim = Tdim[1]
    ttslicenum = Tdim[2]


    for si in range(ttslicenum):
        ROIlist = list()
        xROIlist = list()
        yROIlist = list()

        PIlist = list()
        xPIlist = list()
        yPIlist = list()

        for xi in range(xlistdim):
            for yi in range(ylistdim):

            # in matlab, coordinate is larger than python for 1 pixel, they give slicenum, we define the x and y,
            # T2array starts from 0 after being imported

                ROIvalue = TROIarray[yi,xi,si]

                if ROIvalue!=0:
                    yROIlist.append(yi+1)
                    xROIlist.append(xi+1)
                    ROIlist.append(ROIvalue)


        for xi in range(xlistdim):
            for yi in range(ylistdim):

                PIvalue = TPIarray[yi,xi,si]

                if PIvalue !=0:
                    yPIlist.append(yi+1)
                    xPIlist.append(xi+1)
                    PIlist.append(PIvalue)

        # plt.figure(figsize=(18, 13))
        plt.figure()


        # first cover PI colormap inside
        PIcm = plt.cm.get_cmap('jet')
        plt.scatter(xPIlist, yPIlist, c=PIlist, vmin=0, vmax=1, cmap=PIcm)

        plt.colorbar()

        # then cover ROI colormap inside
        ROIcm = plt.cm.get_cmap('Reds')
        plt.scatter(xROIlist,yROIlist,c=ROIlist,vmin=0, vmax=1, cmap=ROIcm)


        plt.title(casefolder+' slice '+ str(si+1) + ' '+'T1 ROI overlap PI',fontsize=20)
        plt.savefig(caseoutDir + '/'+casefolder+' slice'+ str(si+1) + ' '+'T1 ROI overlap PI.png')

        plt.cla()
        plt.close()

def drawTColormaps(dir,outDir):
    for casefolder in os.listdir(dir):
        if fnmatch.fnmatch(casefolder,"*.dropbox*"):
            continue

        if fnmatch.fnmatch(casefolder,'*.DS_Store*'):
            continue

        if fnmatch.fnmatch(casefolder,'*Icon*'):
            continue

        print casefolder

        casefolderdir = os.path.join(dir,casefolder)


        T1ROImat = 'T1Gd.mat'
        T1PI = casefolder + '_fromT1Gd.mat'


        T1ROIfiledir = os.path.join(casefolderdir,T1ROImat)
        T1PIdir = os.path.join(casefolderdir,T1PI)

        caseoutDir =os.path.join(outDir,casefolder)

        if not os.path.exists(caseoutDir):
            os.makedirs(caseoutDir)


        drawColorMap(T1ROIfiledir,T1PIdir,caseoutDir, casefolder)


drawTColormaps(dir,outDir)




