import csv
import fnmatch
import os

import SimpleITK
import numpy
import matplotlib.pyplot as plt
from scipy.stats import kurtosis
from scipy.stats import skew

import scipy
#from Mahotas.mahotas.features.texture import haralick_labels
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures
from LBP import LBPFeatures
from Gabor import KRAS_GaborFeatures


# Image Root Dir
rootDir ='/Users/yanzhexu/Desktop/Research/0130/ROIs'

outputDir = '/Users/yanzhexu/Desktop/Research/0130/Textures'

filename = 'KRAS_Textures_file.csv'

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
    print imgArray.shape
    if len(imgArray.shape) == 3:

        # set z = 0
        imgArray = imgArray[:, :, 0]

    # print imgArray.shape
    #
    # print imgArray
    # (115,99)

    # has done gray scale normalization before

    # plt.imshow(imgArray,cmap='gray')
    # plt.show()
    return imgArray



def genTextures():

    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

    LBPRadius = 1
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP_%02d' % x)
    LBPFeatureList.append('LBP_Other')

    Gaborsigma_range = (1.0, 2.0)
    Gaborfreq_range = (0.1, 0.3, 0.5)
    kernel_bank = []

    Gaborkernel_bank = ExtendGaborFeatures.genKernelBank(Gaborsigma_range, Gaborfreq_range, kernel_bank)

    GaborFeatureList = ['Gabor_Mean', 'Gabor_Std']

    # Generate full list of features combined with parameters
    featureTitle = ['PatientID']

    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    featureTitle = featureTitle + LBPFeatureList

    for GaborSigma in Gaborsigma_range:
        for GaborFreq in Gaborfreq_range:
            for featureName in GaborFeatureList:
                featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    MeanStdLBfeaturelist = ['Raw_Mean', 'Raw_Std']
    featureTitle = featureTitle + MeanStdLBfeaturelist


    featuresCSVFn = os.path.join(outputDir, filename)
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

            # casefile = '20586908_0.jpg'
            casename = casefile.split('.')[0]
            print casename

            casefilepath = os.path.join(rootDir,casefile)
            subImage = Read2DImage(casefilepath)

            # height = subImage.shape[1]
            # width = subImage.shape[0]
            #
            # xcoord = 5
            # ycoord = 5

            # subImage = dicomImage[ycoord:(ycoord + height), xcoord:(xcoord + width)]  # errors here: before: Y + W
            #
            # subImageLBP = dicomImage[ycoord - LBPRadius:(ycoord + height) + LBPRadius,
            #               xcoord - LBPRadius:(xcoord + width) + LBPRadius]

            # subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

            # for extended LBP, we still use grayscale range of 8*8 box to normalize extended ROI 10*10 box
            # extendsubImageLBP = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

            aFeature = [casename]

            ## get mean and standard deviation of lesion ROI's gray level of lagest box directly from subImage
            Raw_mean = numpy.mean(subImage)
            Raw_std = numpy.std(subImage)

            # SubImagelist = list()
            # SubImageArraylist = subImage.tolist()
            # for smalllist in SubImageArraylist:
            #     SubImagelist += smalllist
            #
            # Raw_kurtosis = kurtosis(SubImagelist)
            # Raw_skewness = skew(SubImagelist)


            # GLCM
            glcmFeatures = GLCMFeatures.calcFeatures(subImage)

            # print glcmFeatures

            for GLCMAngle in GLCMAngleList:
                for featureName in haralick_labels[:-1]:
                    aFeature.append(glcmFeatures[GLCMAngle][featureName])

            # LBP
            lbpFeatures = ExtendLBPFeatures.calcFeatures(subImage, LBPnPoints, LBPRadius, LBPMethod)

            # print lbpFeatures

            aFeature = aFeature + lbpFeatures.tolist()

            # Gabor
            GaborFeatures = KRAS_GaborFeatures.calcFeatures(subImage, Gaborkernel_bank)

            # GaborFeatures = GB.calcFeatures(subImage,Gaborsigma_range,Gaborfreq_range)
            #
            for gaborfeature in GaborFeatures:
                aFeature = aFeature + gaborfeature.tolist()
            #
            aFeature = aFeature + [Raw_mean, Raw_std]
            featureWriter.writerow(aFeature)


genTextures()








