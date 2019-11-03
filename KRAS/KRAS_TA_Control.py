# get Max and Min from only control

import os
import csv
import fnmatch
import SimpleITK
import numpy

from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures

# Image Root Dir
rootDir ='/Users/yanzhexu/Desktop/Research/KRAS/Feb. 2017'

outputDir = '/Users/yanzhexu/Desktop/Research/KRAS/Final_results'

featuresOutFn = 'KRAS_features_normalbyControl_LBP3.csv'

recfile = 'largest_rec.csv'
dcmfile = 'image.dcm'


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


def genFeatures():

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
    featureTitle = ['PatientID', 'Phase', 'ROI_X', 'ROI_Y', 'Width', 'Height']
    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    featureTitle = featureTitle + LBPFeatureList

    for GaborSigma in Gaborsigma_range:
        for GaborFreq in Gaborfreq_range:
            for featureName in GaborFeatureList:
                featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    MeanStdLBfeaturelist = ['LargestBox_Raw_Mean', 'LargestBox_Raw_Std']
    featureTitle = featureTitle + MeanStdLBfeaturelist

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

            if fnmatch.fnmatch(casefile,'*xlsx*'):
                continue

            print casefile

            patientID = casefile.split('_ ')[0]
            print patientID

            patientfilepath = os.path.join(rootDir,casefile)

            phaseDir = dict()
            for patientPhaseDir in os.listdir(patientfilepath):
                if patientPhaseDir.startswith('.'):
                    continue
                if patientPhaseDir.startswith('..'):
                    continue
                if fnmatch.fnmatch(patientPhaseDir, '*Icon*'):
                    continue

                if fnmatch.fnmatch(patientPhaseDir, '*Lesion*'):
                    phaseDir['lesion'] = patientPhaseDir

                    print patientPhaseDir

                if fnmatch.fnmatch(patientPhaseDir, '*Control*'):
                    phaseDir['control'] = patientPhaseDir
                    phasename = patientPhaseDir

                    print patientPhaseDir

            # lesionfile = os.path.join(patientfilepath, phaseDir['lesion'])
            # lesionlargestrecpath = os.path.join(lesionfile, recfile)
            # lesionDicom = os.path.join(lesionfile, dcmfile)

            normalfile = os.path.join(patientfilepath, phaseDir['control'])
            normallargestrecpath = os.path.join(normalfile, recfile)
            normalDicom = os.path.join(normalfile, dcmfile)

            with open(normallargestrecpath, 'r') as roiFile:
                roiList = csv.DictReader(roiFile, dialect='excel')

                for aROI in roiList:

                    xcoord = int(aROI['X'])
                    ycoord = int(aROI['Y'])
                    width = int(aROI['W'])
                    height = int(aROI['H'])

                #lesiondicomImage = Read2DImage(lesionDicom)
                normaldicomImage = Read2DImage(normalDicom)

                # lesionsubImage = lesiondicomImage[ycoord:(ycoord + height), xcoord:(xcoord + width)]
                normalsubImage = normaldicomImage[ycoord:(ycoord + height), xcoord:(xcoord + width)]

                mean_LargBox = numpy.mean(normalsubImage)
                std_LargBox = numpy.std(normalsubImage)

                # get max gray scale and min grayscale from both lesion and normal dicom
                subImageMax = normalsubImage.max()
                subImageMin = normalsubImage.min()

                subImageLBP = normaldicomImage[ycoord - LBPRadius:(ycoord + height) + LBPRadius,
                              xcoord - LBPRadius:(xcoord + width) + LBPRadius]

                subImageGLCM = GrayScaleNormalization(normalsubImage, subImageMax, subImageMin)

                aFeature = [patientID, phasename, aROI['X'], aROI['Y'], aROI['W'], aROI['H']]

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
                GaborFeatures = ExtendGaborFeatures.calcFeatures(normaldicomImage, xcoord, ycoord, width, height,
                                                                 Gaborkernel_bank, subImageMax, subImageMin)

                for gaborfeature in GaborFeatures:
                    aFeature = aFeature + gaborfeature.tolist()

                aFeature = aFeature + [mean_LargBox, std_LargBox]

                featureWriter.writerow(aFeature)

genFeatures()
