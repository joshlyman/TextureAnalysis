import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK


dir = '/Users/yanzhexu/Dropbox/EOR_ML_PI_Shared Regridded_Data/'

outDir = '/Users/yanzhexu/Desktop/Research/EOR_Andrea/EOR_PI_featuresMap_from_Andrea/T1T2overDicom/'

def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


def drawColorMap(T1file,T2file,T2dicomdir, caseoutDir,casefolder):

    Tmat = sio.loadmat(T1file)
    TPImat = sio.loadmat(T2file)


    # 0 or 1 inside
    T1ROIarray = Tmat['T1Gd']

    T2ROIarray = TPImat['T2']

    Tdim = np.shape(T1ROIarray)

    ylistdim = Tdim[0]
    xlistdim = Tdim[1]
    ttslicenum = Tdim[2]


    for si in range(ttslicenum):
        ROI1list = list()
        xROI1list = list()
        yROI1list = list()

        ROI2list = list()
        xROI2list = list()
        yROI2list = list()

        for xi in range(xlistdim):
            for yi in range(ylistdim):

            # in matlab, coordinate is larger than python for 1 pixel, they give slicenum, we define the x and y,
            # T2array starts from 0 after being imported

                ROI1value = T1ROIarray[yi,xi,si]

                if ROI1value!=0:
                    yROI1list.append(yi+1)
                    xROI1list.append(xi+1)
                    ROI1list.append(ROI1value)

        for xi in range(xlistdim):
            for yi in range(ylistdim):

                # in matlab, coordinate is larger than python for 1 pixel, they give slicenum, we define the x and y,
                # T2array starts from 0 after being imported

                ROI2value = T2ROIarray[yi, xi, si]

                if ROI2value != 0:
                    yROI2list.append(yi+1)
                    xROI2list.append(xi+1)
                    ROI2list.append(ROI2value)

        # dicom name should be real name, which is python name + 1
        dicomfile = casefolder+'T2_' + str(si+1) + '.dcm'
        T2dicomfile = os.path.join(T2dicomdir,dicomfile)

        # for JR, T2 dicom file name differs with others
        if not os.path.exists(T2dicomfile):
            dicomfile = casefolder + '_T2_'+str(si+1) + '.dcm'
            T2dicomfile = os.path.join(T2dicomdir,dicomfile)

        # plt.figure(figsize=(18, 13))
        plt.figure()

        # first cover T2 ROI
        ROI2cm = plt.cm.get_cmap('Blues')
        plt.scatter(xROI2list, yROI2list, c=ROI2list, vmin=0, vmax=1, cmap=ROI2cm)

        # then cover T1 ROI
        ROI1cm = plt.cm.get_cmap('Reds')
        plt.scatter(xROI1list,yROI1list,c=ROI1list,vmin=0, vmax=1, cmap=ROI1cm)

        plt.colorbar()

        dicomImage = Read2DImage(T2dicomfile)
        plt.imshow(dicomImage,cmap='gray')

        plt.title(casefolder+' slice '+ str(si+1) + ' '+'T1 T2 ROI overlap Dicom',fontsize=15)
        plt.savefig(caseoutDir + '/'+casefolder+' slice'+ str(si+1) + ' '+'T1 T2 ROI overlap Dicom.png')

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
        T2ROImat = 'T2fill.mat'


        T1ROIfiledir = os.path.join(casefolderdir,T1ROImat)
        T2ROIfiledir = os.path.join(casefolderdir,T2ROImat)
        T2ROIdicomdir = os.path.join(casefolderdir,'T2')


        caseoutDir =os.path.join(outDir,casefolder)

        if not os.path.exists(caseoutDir):
            os.makedirs(caseoutDir)


        drawColorMap(T1ROIfiledir,T2ROIfiledir,T2ROIdicomdir,caseoutDir, casefolder)

drawTColormaps(dir,outDir)
