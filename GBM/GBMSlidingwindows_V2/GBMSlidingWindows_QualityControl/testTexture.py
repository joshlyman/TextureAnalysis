import csv
import fnmatch
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22/+C_3D_AXIAL_IRSPGR_Fast_IM-0005-0022.dcm'

outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/'

featuresOutFn = 'test2.csv'


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


def genTextures():

    GLCMAngleList = ['Avg']
    featureTitle = ['X', 'Y']

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
    featureTitle = featureTitle + MeanStdfeaturelist

    featuresCSVFn = os.path.join(outputDir, featuresOutFn)

    with open(featuresCSVFn, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')
        featureWriter.writerow(featureTitle)

        meanstd = list()
        # GLCM = list()
        # LBP = list()
        # Gabor = list()

        xcoord = 151
        ycoord = 83
        dicomImage = Read2DImage(rootDir)

        aFeature = [xcoord, ycoord]

        subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

        subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

        # GLCM
        glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

        for GLCMAngle in GLCMAngleList:
            for featureName in haralick_labels[:-1]:
                aFeature.append(glcmFeatures[GLCMAngle][featureName])

        # raw mean and std of subimage
        Raw_mean = numpy.mean(subImage)
        Raw_std = numpy.std(subImage)

        meanstd.append(Raw_mean)
        meanstd.append(Raw_std)

        # LBP subimage
        subImageLBP = dicomImage[ycoord - 4 - LBPRadius:ycoord + 4 + LBPRadius,
                      xcoord - 4 - LBPRadius: xcoord + 4 + LBPRadius]

        extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImage.max(),
                                                   subImage.min())

        # need to use extended ROI
        LBPs = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius,
                                              LBPMethod)
        aFeature = aFeature + LBPs.tolist()

        # Gabor, width = 8
        # use extended ROI
        GaborFeatures = ExtendGaborFeatures.calcFeatures(dicomImage, xcoord - 4, ycoord - 4,
                                                         8, 8,
                                                         Gaborkernel_bank, subImage.max(),
                                                         subImage.min())

        for gaborfeature in GaborFeatures:
            aFeature = aFeature + gaborfeature.tolist()

        aFeature = aFeature + meanstd
        featureWriter.writerow(aFeature)

genTextures()