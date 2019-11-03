#!/usr/bin/env python
#=========================================================================
#
# Extract texture features from a region-of-interest within a HCC normal dicom image
# (normal dicom normalized by itself)
#
#=========================================================================

# log
#
#
# To do list:
# 1. fix error on whole code;
# 2. directly use dicom image to get gray scale, not from coords. txt
# 3. fix Gabor features, put newest features in folder



import csv
import fnmatch
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures


def Mean_Std_LargestBox2(dicomimage,largeX,largeY,largeW,largeH):

    largeX2 = largeX + largeW
    largeY2 = largeY + largeH
    LargeBoxGrayLevel = list()
    for x in range(largeX,largeX2):
        for y in range(largeY,largeY2):
            graylevel = dicomimage[y,x]
            LargeBoxGrayLevel.append(graylevel)
    meang = numpy.mean(LargeBoxGrayLevel)
    stdg = numpy.std(LargeBoxGrayLevel)

    return meang,stdg

def GrayScaleNormalization(imgArray, imgRange):
    if imgRange == 0:
        return imgArray

    imgMin = imgArray.min()
    imgArray = (imgArray - imgMin) * (256.0 / imgRange)

    return numpy.rint(imgArray).astype(numpy.int16)


def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


# Image Root Dir
rootDir = '/Users/yanzhexu/Desktop/Research/HCC/HCCVariant (MR - Al)'
outputDir = '/Users/yanzhexu/Desktop/Research/HCC/HCC_Out'


normalDicomFn = 'image.dcm'
roiCoordsFn = 'coords.txt'

featuresOutFn = 'HCC_features_Normal_LBP_3.csv'


def genFeatures():
    # dualRescaleOption: whether use both lesion and normal ROI for grayscale normalization
    # If 'False', use only lesion image
    # default value is 'True'


    # Parameters and feature list of each algorithm
    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

    LBPRadius = 3
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP_%02d' % x)
    LBPFeatureList.append('LBP_Other')

    kernel_bank = []
    Gaborsigma_range = [0.6]
    Gaborfreq_range = (0.1, 0.3, 0.5)

    Gaborkernel_bank = ExtendGaborFeatures.genKernelBank(Gaborsigma_range, Gaborfreq_range, kernel_bank)

    GaborFeatureList = ['Gabor_Mean', 'Gabor_Std']

    # Generate full list of features combined with parameters
    featureTitle = ['PatientID', 'Phase', 'NormalName','ROI_Y', 'ROI_X', 'Width', 'Height']
    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    featureTitle = featureTitle + LBPFeatureList

    for GaborSigma in Gaborsigma_range:
        for GaborFreq in Gaborfreq_range:
            for featureName in GaborFeatureList:
                featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    MeanStdLBfeaturelist = ['LargestBox_Mean', 'LargestBox_Std']
    featureTitle = featureTitle + MeanStdLBfeaturelist

    # List all dicom files and generate features for each images
    # Feature results stored in separate csv files for each folder
    featuresCSVFn = os.path.join(outputDir, featuresOutFn)
    with open(featuresCSVFn, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')
        featureWriter.writerow(featureTitle)

        for casefile in os.listdir(rootDir):
            if casefile.startswith('.'):
                continue
            if casefile.startswith('..'):
                continue
            if fnmatch.fnmatch(casefile, '*Icon*'):
                continue

            print casefile

            patientid = casefile.split('_')[1] + casefile.split('_')[2]

            splitlist = casefile.split('_')

            phasename = ''
            for item in splitlist[3:len(splitlist)]:
                phasename = phasename + ' ' + item

            print patientid
            print phasename

            phasefilepath = os.path.join(rootDir, casefile)

            normalfolder = []

            for phasefile in os.listdir(phasefilepath):
                if phasefile.startswith('.'):
                    continue
                if phasefile.startswith('..'):
                    continue
                if fnmatch.fnmatch(phasefile, '*Icon*'):
                    continue
                if fnmatch.fnmatch(phasefile, '*Normal_Liver*') or fnmatch.fnmatch(phasefile,'*Normal_Liver*') or fnmatch.fnmatch(phasefile, '*liver*'):
                    normalfolder.append(phasefile)

            print normalfolder

            for normalfolderfile in normalfolder:
                normalPath = os.path.join(rootDir, casefile, normalfolderfile)

                for roifile in os.listdir(normalPath):
                    if roifile.startswith('.'):
                        continue
                    if roifile.startswith('..'):
                        continue
                    if fnmatch.fnmatch(roifile, '*Icon*'):
                        continue
                    if fnmatch.fnmatch(roifile, '*rec.csv'):
                        normalroiFn = roifile
                        # Largest rectangle file name with absolute path
                        normalROIRectFn = os.path.join(normalPath, normalroiFn)

                # DICOM file name with absolute path
                normalDicom = os.path.join(normalPath, normalDicomFn)

                # ROI file name with absolute path
                normalROICoords = os.path.join(normalPath, roiCoordsFn)

                dualROIGrayLevels = numpy.array([])
                with open(normalROICoords, 'r') as roiCoordsFile:
                    roiCoordsList = csv.reader(roiCoordsFile, delimiter=';')
                    for row in roiCoordsList:
                        dualROIGrayLevels = numpy.append(dualROIGrayLevels, int(row[2]))

                with open(normalROIRectFn, 'r') as roiFile:
                    roiList = csv.DictReader(roiFile, dialect='excel')
                    for aROI in roiList:
                        if (int(aROI['Y']) == 1) and (int(aROI['X']) == 1):
                            print('Invalid ROI for %s @ %s.' % (patientid, phasename))
                            continue

                        # only normal
                        dicomImage = Read2DImage(normalDicom)

                        subImage = dicomImage[int(aROI['Y']):(int(aROI['Y']) + int(aROI['H'])), \
                                   int(aROI['X']):(int(aROI['X']) + int(aROI['W']))]

                        subImageLBP = dicomImage[int(aROI['Y']) - LBPRadius:(int(aROI['Y']) + int(aROI['H'])) + LBPRadius, \
                                      int(aROI['X']) - LBPRadius:(int(aROI['X']) + int(aROI['W'])) + LBPRadius]

                        mean_LargBox, std_LargBox = Mean_Std_LargestBox2(dicomImage, int(aROI['X']), int(aROI['Y']),
                                                                         int(aROI['W']), int(aROI['H']))

                        subImage = GrayScaleNormalization(subImage, dualROIGrayLevels.ptp())

                        extendsubImageLBP = GrayScaleNormalization(subImageLBP,dualROIGrayLevels.ptp())

                        if numpy.all(subImage == 0):
                            print('%s @ %s is all zero.' % (patientid, phasename))
                            continue

                        aFeature = [patientid, phasename,normalfolderfile, aROI['Y'], aROI['X'], aROI['W'], aROI['H']]

                        # GLCM
                        glcmFeatures = GLCMFeatures.calcFeatures(subImage)

                        for GLCMAngle in GLCMAngleList:
                            for featureName in haralick_labels[:-1]:
                                aFeature.append(glcmFeatures[GLCMAngle][featureName])

                        # LBP
                        lbpFeatures = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius, LBPMethod)
                        aFeature = aFeature + lbpFeatures.tolist()

                        # Gabor
                        GaborFeatures = ExtendGaborFeatures.calcFeatures(subImage, int(aROI['W']), Gaborkernel_bank)

                        for gaborfeature in GaborFeatures:
                            aFeature = aFeature + gaborfeature.tolist()

                        aFeature = aFeature + [mean_LargBox, std_LargBox]

                        featureWriter.writerow(aFeature)
    print('Done.')


genFeatures()