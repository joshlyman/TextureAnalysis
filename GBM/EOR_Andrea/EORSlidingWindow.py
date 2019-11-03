import csv
import os
import xml.etree.ElementTree as ET
import fnmatch
import numpy
import math
import SimpleITK
from mahotas.features.texture import haralick_labels
import scipy.io as sio


from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures


dir = '/Users/yanzhexu/Dropbox/EOR_ML_PI_Shared Regridded_Data/'
selectSlicefile = '/Users/yanzhexu/Desktop/Research/EOR_Andrea/EOR_PI_featuresMap_from_Andrea/EOR_Selected_Slice.csv'
outputDir = '/Users/yanzhexu/Desktop/Research/EOR_Andrea/Sliding box EOR/'

def Norm_Mean_Std_LargestBox(imgArray,imgMax,imgMin):

    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    meang = numpy.mean(imgArray)
    stdg = numpy.std(imgArray)

    return meang,stdg

def GrayScaleNormalization(imgArray, imgMax,imgMin):

    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    # transfer to closest int
    imgArray = numpy.rint(imgArray).astype(numpy.int16)

    return imgArray


def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray

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

    Tdim = numpy.shape(Tarray)

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

            # needs to add 1 for both xi and yi because need to recover matlab from python file
            if ROIvalue !=0:
                xlist.append(xi+1)
                ylist.append(yi+1)

                xylist.append(list())
                xylist[len(xylist)-1].append(xi+1)
                xylist[len(xylist)-1].append(yi+1)

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


# load mat file and get PI
def getT2PI(PIfile, xylist,slice):

    PIxylist = list()

    # get PI from PI mat file
    Tmat = sio.loadmat(PIfile)
    Tarray = Tmat['u']

    for xypair in xylist:
        xcoord = int(xypair[0])
        ycoord = int(xypair[1])

        # in python, to get value from matlab must -1
        PIvalue = float(Tarray[ycoord-1,xcoord-1,slice-1])

        xypair.append(PIvalue)
        PIxylist.append(xypair)

    return PIxylist



def genTextures():

    GLCMAngleList = ['Avg']
    featureTitle = ['Image Contrast', 'Image Filename','X', 'Y','T1 window in T2 (1) or not (0)']

    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    LBPRadius = 1
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP_%02d' % x)
    LBPFeatureList.append('LBP_Other')

    featureTitle = featureTitle + LBPFeatureList

    Gaborsigma_range = (0.6,1.0)
    Gaborfreq_range = (0.1, 0.3, 0.5)
    kernel_bank = []
    GaborFeatureList = ['Gabor_Mean', 'Gabor_Std']

    for GaborSigma in Gaborsigma_range:
        for GaborFreq in Gaborfreq_range:
            for featureName in GaborFeatureList:
                featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    Gaborkernel_bank = ExtendGaborFeatures.genKernelBank(Gaborsigma_range, Gaborfreq_range, kernel_bank)

    MeanStdfeaturelist = ['Raw_Mean','Raw_Std']
    PIlabel = ['PI Prediction']
    Ylabel = ['Ylabel']

    featureTitle = featureTitle + MeanStdfeaturelist + PIlabel + Ylabel

    dicomnames = ['T1', 'T2']

    # get selected slice from csv file
    casedict = getcaseslice(selectSlicefile)

    for case in casedict:
        slicelist = casedict[case]
        caseDir = os.path.join(dir, case)
        T1ROIDir = os.path.join(caseDir, 'T1Gd.mat')
        T2ROIDir = os.path.join(caseDir, 'T2fill.mat')

        T2PIfile = case+'_fromT2.mat'
        T2PIDir = os.path.join(caseDir,T2PIfile)

        print case

        for slice in slicelist:
            print "slice:", slice

            T1ROIxlist, T1ROIylist, T1ROIxylist = getSlicepts(T1ROIDir, 'T1', int(slice))
            T2ROIxlist, T2ROIylist, T2ROIxylist = getSlicepts(T2ROIDir, 'T2', int(slice))

            # get all window pts coord: (x,y,T1ornot)
            T1T2ROIxylist = combineT1T2list(T1ROIxylist, T2ROIxylist)

            # get PI from mat files
            T1T2ROIPIxylist = getT2PI(T2PIDir,T1T2ROIxylist,int(slice))

            # get dcm file from T1Gd folder
            T1dcmfilename = case+'T1Gd_'+slice+'.dcm'
            T1dcmpath = os.path.join(caseDir,'T1Gd')
            T1dcmfile = os.path.join(T1dcmpath,T1dcmfilename)

            if not os.path.exists(T1dcmfile):
                T1dcmfilename = case+'_T1Gd_'+slice + '.dcm'
                T1dcmfile = os.path.join(T1dcmpath,T1dcmfilename)

            # get dcm file from T2 folder
            T2dcmfilename = case + 'T2_' + slice + '.dcm'
            T2dcmpath = os.path.join(caseDir, 'T2')
            T2dcmfile = os.path.join(T2dcmpath, T2dcmfilename)

            if not os.path.exists(T2dcmfile):
                T2dcmfilename = case + '_T2_' + slice + '.dcm'
                T2dcmfile = os.path.join(T2dcmpath, T2dcmfilename)

            # put dicom file path in dict
            dcmfiledict = dict()

            dcmfiledict['T1'] = T1dcmfile
            dcmfiledict['T2'] = T2dcmfile

            featuresOutFn = 'ROI_Texture_Map.csv'

            T2featuresOutFn = case + '_slice' + slice + '_' + 'T2' + '_' + featuresOutFn
            featuresCSVFn = os.path.join(outputDir, T2featuresOutFn)

            with open(featuresCSVFn, 'wb') as featureCSVFile:
                featureWriter = csv.writer(featureCSVFile, dialect='excel')
                featureWriter.writerow(featureTitle)

                for eachdcm in dicomnames:

                    print eachdcm
                    dicomfilepath = dcmfiledict[eachdcm]

                    dicomImage = Read2DImage(dicomfilepath)

                    if eachdcm =='T1':
                        dicomfile = T1dcmfilename
                    else:
                        dicomfile = T2dcmfilename

                    for eachpt in T1T2ROIPIxylist:

                        meanstd = list()
                        GLCM = list()
                        LBP = list()
                        Gabor = list()

                        xcoord = int(eachpt[0])
                        ycoord = int(eachpt[1])
                        T1ornot = int(eachpt[2])
                        PIvalue = float(eachpt[3])

                        PIv = [PIvalue]

                        aFeature = [eachdcm, dicomfile, xcoord, ycoord, T1ornot]

                        subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

                        subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

                        # Raw_mean = numpy.mean(subImage)
                        # Raw_std = numpy.std(subImage)

                        ## get normalized to 0, 255: raw mean and standard deviation
                        dicommean, dicomstd = Norm_Mean_Std_LargestBox(subImage, subImage.max(), subImage.min())

                        meanstd.append(dicommean)
                        meanstd.append(dicomstd)

                        # GLCM
                        glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

                        for GLCMAngle in GLCMAngleList:
                            for featureName in haralick_labels[:-1]:
                                GLCM.append(glcmFeatures[GLCMAngle][featureName])

                        # LBP subimage
                        subImageLBP = dicomImage[ycoord - 4 - LBPRadius:ycoord + 4 + LBPRadius,
                                      xcoord - 4 - LBPRadius: xcoord + 4 + LBPRadius]

                        extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImage.max(),
                                                                   subImage.min())

                        # need to use extended ROI
                        LBPs = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius,
                                                              LBPMethod)
                        for lbp in LBPs:
                            LBP.append(lbp)

                        # Gabor, width = 8
                        # use extended ROI
                        GaborFeatures = ExtendGaborFeatures.calcFeatures(dicomImage, xcoord - 4, ycoord - 4,
                                                                         8, 8,
                                                                         Gaborkernel_bank, subImage.max(),
                                                                         subImage.min())

                        for gaborfeature in GaborFeatures:
                            for eachg in gaborfeature:
                                Gabor.append(eachg)

                        aFeature = aFeature + GLCM + LBP + Gabor + meanstd + PIv
                        featureWriter.writerow(aFeature)

genTextures()








