import csv
import fnmatch
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from LBP import ExtendLBPFeatures


def Mean_Std_LargestBox2(dicomimage,largeX,largeY,largeW,largeH):
    # if phasename == 'LE-MLO':
    largeX2 = largeX + largeW
    largeY2 = largeY + largeH
    LargeBoxGrayLevel = list()
    for x in range(largeX,largeX2):
        for y in range(largeY,largeY2):
            graylevel = dicomimage[y,x]
            LargeBoxGrayLevel.append(graylevel)
    meang = numpy.mean(LargeBoxGrayLevel)
    stdg = numpy.std(LargeBoxGrayLevel)
    # print meang
    # print stdg
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
rootDir = '/Users/yanzhexu/Desktop/Research/Prostate/Output'
outputDir = '/Users/yanzhexu/Desktop/Research/Prostate_Out'

lesionFolder = 'Lesion'
normalFolder = 'Control'
lesionDicomFn = 'image.dcm'
normalDicomFn = 'image.dcm'
roiCoordsFn = 'coords.txt'
lesionroiFn = 'Lesion_image_largest_rec.csv'
normalroiFn = 'Control_image_largest_rec.csv'
featuresOutFn = 'Prostate_features_Lesion.csv'


def genFeatures():
    # dualRescaleOption: whether use both lesion and normal ROI for grayscale normalization
    # If 'False', use only lesion image
    # default value is 'True'


    # Parameters and feature list of each algorithm
    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

    LBPRadius = 1
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP_%02d' % x)
    LBPFeatureList.append('LBP_Other')


    # Generate full list of features combined with parameters
    featureTitle = ['PatientID', 'Phase', 'ROI_Y', 'ROI_X', 'Width', 'Height']
    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    featureTitle = featureTitle + LBPFeatureList

    MeanStdLBfeaturelist = ['LargestBox_Mean', 'LargestBox_Std']
    featureTitle = featureTitle + MeanStdLBfeaturelist

    # List all dicom files and generate features for each images
    # Feature results stored in separate csv files for each folder
    featuresCSVFn = os.path.join(outputDir, featuresOutFn)
    with open(featuresCSVFn, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')
        featureWriter.writerow(featureTitle)

        for patientPhaseDir in os.listdir(rootDir):
            if patientPhaseDir.startswith('.') or \
                    os.path.isfile(os.path.join(rootDir, patientPhaseDir)):
                continue

            print patientPhaseDir

            if fnmatch.fnmatch(patientPhaseDir, '*20160212*'):
                patientID = '20160212'
            else:
                patientID = patientPhaseDir.split('_')[2]

            if fnmatch.fnmatch(patientPhaseDir, '*ADC*'):
                phasename = 'ADC'
            elif fnmatch.fnmatch(patientPhaseDir, '*TRACEW*'):
                phasename = 'TRACEW'
            else:
                phasename = 'FOV'

            #print('Processing %s @ %s ...' % (patientID, phaseName))

            lesionPath = os.path.join(rootDir, patientPhaseDir, lesionFolder)
            normalPath = os.path.join(rootDir, patientPhaseDir, normalFolder)

            # DICOM file name with absolute path
            lesionDicom = os.path.join(lesionPath, lesionDicomFn)
            normalDicom = os.path.join(normalPath, normalDicomFn)

            # ROI file name with absolute path
            lesionROICoords = os.path.join(lesionPath, roiCoordsFn)
            normalROICoords = os.path.join(normalPath, roiCoordsFn)

            # Largest rectangle file name with absolute path
            lesionROIRectFn = os.path.join(lesionPath, lesionroiFn)
            normalRoiRectFn = os.path.join(normalPath,normalroiFn)

            if (not os.path.isfile(lesionDicom)) or \
                    (not os.path.isfile(normalDicom)) or \
                    (not os.path.isfile(lesionROICoords)) or \
                    (not os.path.isfile(normalROICoords)) or \
                    (not os.path.isfile(normalROICoords)):  # If any of the file is missing, skip
                print('Missing File for %s @ %s.' % (patientID, phasename))
                continue

            dualROIGrayLevels = numpy.array([])
            with open(lesionROICoords, 'r') as roiCoordsFile:
                roiCoordsList = csv.reader(roiCoordsFile, delimiter=';')
                for row in roiCoordsList:
                    dualROIGrayLevels = numpy.append(dualROIGrayLevels, int(row[2]))

            with open(lesionROIRectFn, 'r') as roiFile:
                roiList = csv.DictReader(roiFile, dialect='excel')
                for aROI in roiList:
                    if (int(aROI['Y']) == 1) and (int(aROI['X']) == 1):
                        print('Invalid ROI for %s @ %s.' % (patientID, phasename))
                        continue

                    # only normal

                    dicomImage = Read2DImage(lesionDicom)

                    subImage = dicomImage[int(aROI['Y']):(int(aROI['Y']) + int(aROI['H'])), \
                               int(aROI['X']):(int(aROI['X']) + int(aROI['W']))]

                    subImageLBP = dicomImage[int(aROI['Y']) - LBPRadius:(int(aROI['Y']) + int(aROI['H'])) + LBPRadius, \
                                  int(aROI['X']) - LBPRadius:(int(aROI['X']) + int(aROI['W'])) + LBPRadius]

                    mean_LargBox, std_LargBox = Mean_Std_LargestBox2(dicomImage, int(aROI['X']), int(aROI['Y']),
                                                                     int(aROI['W']), int(aROI['H']))

                    subImage = GrayScaleNormalization(subImage, dualROIGrayLevels.ptp())

                    extendsubImageLBP = GrayScaleNormalization(subImageLBP,dualROIGrayLevels.ptp())

                    if numpy.all(subImage == 0):
                        print('%s @ %s is all zero.' % (patientID, phasename))
                        continue

                    aFeature = [patientID, phasename, aROI['Y'], aROI['X'], aROI['W'], aROI['H']]

                    # GLCM
                    glcmFeatures = GLCMFeatures.calcFeatures(subImage)

                    for GLCMAngle in GLCMAngleList:
                        for featureName in haralick_labels[:-1]:
                            aFeature.append(glcmFeatures[GLCMAngle][featureName])

                    # LBP
                    lbpFeatures = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius, LBPMethod)
                    aFeature = aFeature + lbpFeatures.tolist()

                    aFeature = aFeature + [mean_LargBox, std_LargBox]

                    featureWriter.writerow(aFeature)
    print('Done.')


genFeatures()