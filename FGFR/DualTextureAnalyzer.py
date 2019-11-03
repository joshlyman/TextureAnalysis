# Main code: get normalization range from both lesion and normal

import csv
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import LBPFeatures
from LOGH import LoGHistogramFeatures


def GrayScaleNormalization(imgArray, imgRange,imgMin):
    if imgRange == 0:
        return imgArray
    
    #imgMin = imgRange.min() # problem here: should be imgArray.min()
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)
    
    return numpy.rint(imgArray).astype(numpy.int16)
    
def Read2DImage(fileName, rotateAngle = 0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)
    
    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]
    
    return imgArray

# Image Root Dir
rootDir = '/Users/yanzhexu/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2'
outputDir = '/Users/yanzhexu/Desktop/Research/FGFR2'

lesionFolder  = 'Lesion'
normalFolder  = 'Normal_Liver'
lesionDicomFn = 'image.dcm'
normalDicomFn = 'image.dcm'
roiCoordsFn   = 'coords.txt'
roiFn         = 'image_largest_rec.csv'
featuresOutFn = 'FGFR2_features_2.csv'

def genFeatures(dualRescaleOption = True):
    # dualRescaleOption: whether use both lesion and normal ROI for grayscale normalization
    # If 'False', use only lesion image
    # default value is 'True'


    # Parameters and feature list of each algorithm
    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

    LBPRadius = 1
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'
    LBPnBins = 12

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP_%02d' % x)
    LBPFeatureList.append('LBP_Other')
        
    LoGHSigmaList = numpy.arange(2, 7, 2, dtype = numpy.float)
    LogHFeatureList = ['LoGH_Mean', 'LoGH_Variance', 'LoGH_Skewness', 'LoGH_Kurtosis', 'LoGH_Entropy', 'LoGH_Uniformity']

    Gaborsigma_range = numpy.arange(1, 6, 2)
    Gaborfreq_range = numpy.round(numpy.arange(0.1, 0.6, 0.2), 2)

    kernel_bank = []

    Gaborkernel_bank = ExtendGaborFeatures.genKernelBank(Gaborsigma_range, Gaborfreq_range, kernel_bank)

    # GaborSigmaRange = (1.0, 3.0)
    # GaborFreqRange = (0.1, 0.3, 0.5)
    GaborFeatureList = ['Gabor_Mean', 'Gabor_Std']

    # Generate full list of features combined with parameters
    featureTitle = ['PatientID', 'Phase', 'ROI_Y', 'ROI_X', 'Width', 'Height']
    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    featureTitle = featureTitle + LBPFeatureList
    
    for LoGHSigma in LoGHSigmaList:
        for featureName in LogHFeatureList:
            featureTitle.append(featureName + '_' + str(LoGHSigma))

    for GaborSigma in Gaborsigma_range:
        for GaborFreq in Gaborfreq_range:
            for featureName in GaborFeatureList:
                featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    # List all dicom files and generate features for each images
    # Feature results stored in separate csv files for each folder
    featuresCSVFn = os.path.join(outputDir, featuresOutFn)
    with open(featuresCSVFn, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect = 'excel')
        featureWriter.writerow(featureTitle)

        for patientPhaseDir in os.listdir(rootDir):
            if patientPhaseDir.startswith('.') or \
               os.path.isfile(os.path.join(rootDir, patientPhaseDir)):
                continue

            patientID = patientPhaseDir.split('_ ')[0]
            phaseName = patientPhaseDir.split('_ ')[1].split('_')[1] # Only a simple parser, not always precise
            
            print('Processing %s @ %s ...' % (patientID, phaseName) )

            lesionPath = os.path.join(rootDir, patientPhaseDir, lesionFolder)
            normalPath = os.path.join(rootDir, patientPhaseDir, normalFolder)

            # DICOM file name with absolute path
            lesionDicom = os.path.join(lesionPath, lesionDicomFn)
            normalDicom = os.path.join(normalPath, normalDicomFn)

            # ROI file name with absolute path
            lesionROICoords = os.path.join(lesionPath, roiCoordsFn)
            normalROICoords = os.path.join(normalPath, roiCoordsFn)

            # Largest rectangle file name with absolute path
            lesionROIRectFn = os.path.join(lesionPath, roiFn)

            if (not os.path.isfile(lesionDicom)) or \
               (not os.path.isfile(normalDicom)) or \
               (not os.path.isfile(lesionROICoords)) or \
               (not os.path.isfile(normalROICoords)) or \
               (not os.path.isfile(normalROICoords)): # If any of the file is missing, skip
                    print('Missing File for %s @ %s.'%(patientID, phaseName))
                    continue

            dualROIGrayLevels = numpy.array([])
            with open(lesionROICoords, 'r') as roiCoordsFile:
                roiCoordsList = csv.reader(roiCoordsFile, delimiter=';')
                for row in roiCoordsList:
                    dualROIGrayLevels = numpy.append(dualROIGrayLevels, int(row[2]))
            if (dualRescaleOption):
                with open(normalROICoords, 'r') as roiCoordsFile:
                    roiCoordsList = csv.reader(roiCoordsFile, delimiter=';')
                    for row in roiCoordsList:
                        dualROIGrayLevels = numpy.append(dualROIGrayLevels, int(row[2]))

            with open(lesionROIRectFn, 'r') as roiFile:
                roiList = csv.DictReader(roiFile, dialect = 'excel')
                for aROI in roiList:
                    if (int(aROI['Y']) == 1) and (int(aROI['X']) == 1):
                        print('Invalid ROI for %s @ %s.'%(patientID, phaseName))
                        continue

                    dicomImage = Read2DImage(lesionDicom)
                    # subImage = dicomImage[int(aROI['Y']):(int(aROI['Y']) + int(aROI['W'])), \
                    #                       int(aROI['X']):(int(aROI['X']) + int(aROI['H']))]

                    subImage = dicomImage[int(aROI['Y']):(int(aROI['Y']) + int(aROI['H'])), \
                               int(aROI['X']):(int(aROI['X']) + int(aROI['W']))]

                    subImage = GrayScaleNormalization(subImage, dualROIGrayLevels.ptp(),dualROIGrayLevels.min())



                    if numpy.all(subImage == 0):
                        print('%s @ %s is all zero.'%(patientID, phaseName))
                        continue

                    aFeature = [patientID, phaseName, aROI['Y'], aROI['X'], aROI['W'], aROI['H']]
                    
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
                    # for GaborSigma in Gaborsigma_range:
                    #     for GaborFreq in Gaborfreq_range:
                            #gaborFeatures = GaborFeatures.calcFeatures(subImage, GaborSigma, GaborFreq)
                    GaborFeatures = ExtendGaborFeatures.calcFeatures(subImage, int(aROI['W']), Gaborkernel_bank)

                    for gaborfeature in GaborFeatures:
                        aFeature = aFeature + gaborfeature.tolist()

                    featureWriter.writerow(aFeature)
    print('Done.')
  
genFeatures(dualRescaleOption = True)