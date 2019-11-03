# Early code

import csv
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures


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


# Image Root Dir
rootDir = '/Users/yanzhexu/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2'
outputDir = '/Users/yanzhexu/Desktop/Research/FGFR2/Final_results'

lesionFolder = 'Lesion'
normalFolder = 'Normal_Liver'
lesionDicomFn = 'image.dcm'
normalDicomFn = 'image.dcm'
roiCoordsFn = 'coords.txt'
roiFn = 'image_largest_rec.csv'
featuresOutFn = 'FGFR2_features_LBP3_new.csv'


def genFeatures(dualRescaleOption=True):
    # dualRescaleOption: whether use both lesion and normal ROI for grayscale normalization
    # If 'False', use only lesion image
    # default value is 'True'


    # Parameters and feature list of each algorithm
    #GLCMAngleList = ['0', '45', '90', '135', 'Avg']
    GLCMAngleList = ['Avg']

    LBPRadius = 3
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'
    # LBPnBins = 12

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP_%02d' % x)
    LBPFeatureList.append('LBP_Other')

    Gaborsigma_range = (1.0, 3.0)
    Gaborfreq_range = (0.1, 0.3, 0.5)

    kernel_bank = []

    Gaborkernel_bank = ExtendGaborFeatures.genKernelBank(Gaborsigma_range, Gaborfreq_range, kernel_bank)

    GaborFeatureList = ['Gabor_Mean', 'Gabor_Std']

    # Generate full list of features combined with parameters
    featureTitle = ['PatientID', 'Phase', 'ROI_Y', 'ROI_X', 'Width', 'Height']
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

        for patientPhaseDir in os.listdir(rootDir):
            if patientPhaseDir.startswith('.') or \
                    os.path.isfile(os.path.join(rootDir, patientPhaseDir)):
                continue

            patientID = patientPhaseDir.split('_ ')[0]
            phaseName = patientPhaseDir.split('_ ')[1].split('_')[1]  # Only a simple parser, not always precise

            print('Processing %s @ %s ...' % (patientID, phaseName))

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
                    (not os.path.isfile(normalROICoords)):  #  If any of the file is missing, skip,
                                                            # To do: problem here

                print('Missing File for %s @ %s.' % (patientID, phaseName))
                continue

            with open(lesionROIRectFn, 'r') as roiFile:
                roiList = csv.DictReader(roiFile, dialect='excel')
                for aROI in roiList:
                    if (int(aROI['Y']) == 1) and (int(aROI['X']) == 1):
                        print('Invalid ROI for %s @ %s.' % (patientID, phaseName))
                        continue

                    lesiondicomImage = Read2DImage(lesionDicom)
                    normaldicomImage = Read2DImage(normalDicom)


                    xcoord = int(aROI['X'])
                    ycoord = int(aROI['Y'])
                    width = int(aROI['W'])
                    height = int(aROI['H'])

                    lesionsubImage = lesiondicomImage[ycoord:(ycoord + height),xcoord:(xcoord + width)]
                    normalsubImage = normaldicomImage[ycoord:(ycoord + height),xcoord:(xcoord + width)]

                    mean_LargBox = numpy.mean(lesionsubImage)
                    std_LargBox = numpy.std(lesionsubImage)

                    # get max gray scale and min grayscale from both lesion and normal dicom
                    lesionimageMax = lesionsubImage.max()
                    lesionimageMin = lesionsubImage.min()
                    normalimageMax = normalsubImage.max()
                    normalimageMin = normalsubImage.min()

                    # compare max and min and get max / min for normalization
                    if lesionimageMax > normalimageMax:
                        subImageMax = lesionimageMax
                    else:
                        subImageMax = normalimageMax

                    if lesionimageMin < normalimageMin:
                        subImageMin = lesionimageMin
                    else:
                        subImageMin = normalimageMin

                    subImageLBP = lesiondicomImage[ycoord - LBPRadius:(ycoord + height) + LBPRadius,
                                  xcoord - LBPRadius:(xcoord + width) + LBPRadius]

                    subImageGLCM = GrayScaleNormalization(lesionsubImage, subImageMax, subImageMin)

                    if numpy.all(lesionsubImage == 0):
                        print('%s @ %s is all zero.' % (patientID, phaseName))
                        continue

                    aFeature = [patientID, phaseName, aROI['Y'], aROI['X'], aROI['W'], aROI['H']]

                    # GLCM
                    glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

                    for GLCMAngle in GLCMAngleList:
                        for featureName in haralick_labels[:-1]:
                            aFeature.append(glcmFeatures[GLCMAngle][featureName])

                    # LBP
                    extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImageMax, subImageMin)

                    lbpFeatures = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius, LBPMethod)
                    aFeature = aFeature + lbpFeatures.tolist()


                    # Gabor
                    GaborFeatures = ExtendGaborFeatures.calcFeatures(lesiondicomImage, xcoord, ycoord, width, height,
                                                                     Gaborkernel_bank, subImageMax, subImageMin)

                    for gaborfeature in GaborFeatures:
                        aFeature = aFeature + gaborfeature.tolist()

                    aFeature = aFeature + [mean_LargBox, std_LargBox]

                    featureWriter.writerow(aFeature)
    print('Done.')


genFeatures(dualRescaleOption=True)