import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK


dir = '/Users/yanzhexu/Dropbox/EOR_ML_PI_Shared Regridded_Data/'

# T1, T2 change here
outDir = '/Users/yanzhexu/Desktop/Research/EOR_Andrea/EOR_PI_featuresMap_from_Andrea/'

def drawColorMap(Tfile,caseoutDir,casefolder,T):

    Tmat = sio.loadmat(Tfile)

    Tarray = Tmat['u']

    Tdim = np.shape(Tarray)


    ylistdim = Tdim[0]
    xlistdim = Tdim[1]
    ttslicenum = Tdim[2]


    for si in range(ttslicenum):
        plist = list()
        xlist = list()
        ylist = list()

        for xi in range(xlistdim):
            for yi in range(ylistdim):

            # in matlab, coordinate is larger than python for 1 pixel, they give slicenum, we define the x and y,
            # T2array starts from 0 after being imported

                pvalue = Tarray[yi,xi,si]

                # need +1
                if pvalue !=0:
                    ylist.append(yi+1)
                    xlist.append(xi+1)
                    plist.append(pvalue)

        # plt.figure(figsize=(18, 13))
        plt.figure()

        cm = plt.cm.get_cmap('jet')

        plt.scatter(xlist, ylist, c=plist, vmin=0, vmax=1, cmap=cm)

        plt.colorbar()

        plt.title(casefolder+' slice '+ str(si+1) + ' '+T+' PI',fontsize=20)
        plt.savefig(caseoutDir + '/'+casefolder+' slice'+ str(si+1) + ' '+T+' PI.png')

        plt.cla()
        plt.close()

def drawTColormaps(dir,outDir,T):
    for casefolder in os.listdir(dir):
        if fnmatch.fnmatch(casefolder,"*.dropbox*"):
            continue

        if fnmatch.fnmatch(casefolder,'*.DS_Store*'):
            continue

        if fnmatch.fnmatch(casefolder,'*Icon*'):
            continue

        print casefolder


        casefolderdir = os.path.join(dir,casefolder)


        T1Matname = casefolder + '_fromT1Gd.mat'
        T2Matname = casefolder + '_fromT2.mat'


        T1filedir = os.path.join(casefolderdir,T1Matname)
        T2filedir = os.path.join(casefolderdir,T2Matname)

        ToutDir = outDir + '/'+ T + 'PI/'
        caseoutDir =os.path.join(ToutDir,casefolder)

        if not os.path.exists(caseoutDir):
            os.makedirs(caseoutDir)

        if T == 'T1':
            drawColorMap(T1filedir, caseoutDir, casefolder,T)
        else:
            drawColorMap(T2filedir, caseoutDir, casefolder,T)


# change T1, T2 here
drawTColormaps(dir,outDir,'T2')




