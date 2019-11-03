import csv
import fnmatch
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import GaborFeatures
from LBP import LBPFeatures
from LOGH import LoGHistogramFeatures


def GrayScaleNormalization(imgArray):
    imgRange = imgArray.ptp()
    if imgRange == 0:
        return imgArray
    
    imgMin = imgArray.min()
    imgArray = (imgArray - imgMin) * (256.0 / imgRange)
    
    return numpy.rint(imgArray).astype(numpy.uint8)
    
def Read2DImage(fileName):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)
    
    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]
        
    return imgArray

# Image Root Dir
# rootDir = '/Users/bigpizza/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2'
rootDir = '/Users/bigpizza/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2 - NewNeg'
# rootDir = '/Users/bigpizza/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2/1FGFR2gene_1095_ 20150608_Venous'

roiExtFn = '_box.csv'
dicomFnMask = '*.dcm'
featuresExtFn = '_features.csv'

ROI_SIZE = 7
ROI_RADIUS = (ROI_SIZE - 1) / 2

def genFeatures():
    # Parameters and feature list of each algorithm
    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

    LBPFeatureList = ['LBP_00', 'LBP_01','LBP_02', 'LBP_03', 'LBP_04', 'LBP_05', \
                      'LBP_06', 'LBP_07', 'LBP_08', 'LBP_09','LBP_10', 'LBP_11']
    LBPRadius = 3
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'
    LBPnBins = 12

    LoGHSigmaList = numpy.arange(2, 7, 2, dtype = numpy.float)
    LogHFeatureList = ['LoGH_Mean', 'LoGH_Variance', 'LoGH_Skewness', 'LoGH_Kurtosis', 'LoGH_Entropy', 'LoGH_Uniformity']

    GaborSigmaRange = (1.0, 3.0)
    GaborFreqRange = (0.6, 1)
    GaborFeatureList = ['Gabor_Mean', 'Gabor_Std']

    # Generate full list of features combined with parameters
    featureTitle = ['FileName', 'ROI_Y', 'ROI_X']
    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    featureTitle = featureTitle + LBPFeatureList
    
    for LoGHSigma in LoGHSigmaList:
        for featureName in LogHFeatureList:
            featureTitle.append(featureName + '_' + str(LoGHSigma))

    for GaborSigma in GaborSigmaRange:
        for GaborFreq in GaborFreqRange:
            for featureName in GaborFeatureList:
                featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    # List all dicom files and generate features for each images
    # Feature results stored in separate csv files for each folder
    for dirPath, dirNames, fileNames in os.walk(rootDir):
        for dicomFn in fnmatch.filter(fileNames, dicomFnMask):
            dicomPath = os.path.join(dirPath, dicomFn)
            roiCSVFn = os.path.join(dirPath, os.path.splitext(dicomFn)[0] + roiExtFn)

            if not os.path.isfile(roiCSVFn):
                print('No ROI File for %s.'%dicomPath)
                continue

            featuresCSVFn = os.path.join(dirPath, os.path.splitext(dicomFn)[0] + featuresExtFn)
            
            with open(featuresCSVFn, 'wb') as featureCSVFile:
                featureWriter = csv.writer(featureCSVFile, dialect = 'excel')
                featureWriter.writerow(featureTitle)
                
                with open(roiCSVFn, 'r') as roiFile:
                    roiList = csv.DictReader(roiFile, dialect = 'excel')
                    for aROI in roiList:
                        if (int(aROI['Y']) == 1) and (int(aROI['X']) == 1):
                            print('Invalid ROI center @ %s.'%dicomPath)
                            continue
                        #else:
                            #print('(%s, %s) @ %s.'%(aROI['Y'], aROI['X'], dicomPath))

                        dicomImage = Read2DImage(dicomPath)
                        subImage = dicomImage[(int(aROI['Y']) - ROI_RADIUS):(int(aROI['Y']) + ROI_RADIUS), \
                                              (int(aROI['X']) - ROI_RADIUS):(int(aROI['X']) + ROI_RADIUS)]
                        subImage = GrayScaleNormalization(subImage)

                        if numpy.all(subImage == 0):
                            print('(%s, %s) @ %s is all zero.'%(dicomFn, aROI['Y'], aROI['X']))
                            continue

                        aFeature = [dicomFn, aROI['Y'], aROI['X']]
                        
                        # GLCM
                        glcmFeatures = GLCMFeatures.calcFeatures(subImage)
                        
                        for GLCMAngle in GLCMAngleList:
                            for featureName in haralick_labels[:-1]:
                                aFeature.append(glcmFeatures[GLCMAngle][featureName])
                        
                        # LBP
                        lbpFeatures = LBPFeatures.calcFeatures(subImage, LBPnPoints, LBPRadius, LBPMethod, LBPnBins)
                        aFeature = aFeature + lbpFeatures.tolist()

                        # LoGH
                        LoGHFeatures = LoGHistogramFeatures.calcFeatures(subImage, LoGHSigmaList)
                        for LoGHFeaturePerSimga in LoGHFeatures:
                            aFeature = aFeature + LoGHFeaturePerSimga.tolist()
                        
                        # Gabor
                        for GaborSigma in GaborSigmaRange:
                            for GaborFreq in GaborFreqRange:
                                gaborFeatures = GaborFeatures.calcFeatures(subImage, GaborSigma, GaborFreq)
                                aFeature = aFeature + gaborFeatures.tolist()

                        featureWriter.writerow(aFeature)

genFeatures()