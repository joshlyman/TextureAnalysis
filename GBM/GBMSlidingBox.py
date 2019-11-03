# GBM sliding windows experiments (only CEFSL slice 22 + JTyFSL slice 15)
#
#


import csv
import fnmatch
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures

def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray

def GrayScaleNormalization(imgArray, imgMax,imgMin):

    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    # transfer to closest int
    imgArray = numpy.rint(imgArray).astype(numpy.int16)

    return imgArray


rootDir = '/Users/yanzhexu/Desktop/Research/GBM/T1 and T2 texture Maps - grid spacing 4/JTyFSL_slice15_T1 ROI_texture_map.csv'
# rootDir = '/Users/yanzhexu/Desktop/Research/GBM/T1 and T2 texture Maps - grid spacing 4/CEFSL_slice22_T1 ROI_texture_map.csv'

#mapfileDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22'

mapfileDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/JTyFSL_slices_only/slice15'

outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/SlidingWindows_Experiments'

#featuresOutFn = 'CEFSL_22_Original.csv'
featuresOutFn = 'JTyFSL_15_Comparison.csv'

GLCMAngleList = ['Avg']

featureTitle = ['image Contrast', 'image file name', 'Y coordinate', 'X coordinate']

for GLCMAngle in GLCMAngleList:
    for featureName in haralick_labels[:-1]:
        featureTitle.append(featureName + '_' + GLCMAngle)

featuresCSVFn = os.path.join(outputDir, featuresOutFn)

with open(featuresCSVFn, 'wb') as featureCSVFile:
    featureWriter = csv.writer(featureCSVFile, dialect='excel')
    featureWriter.writerow(featureTitle)

    with open(rootDir, 'r') as roiFile:

        for i in range(9):
            roiFile.readline()

        rowFile = csv.reader(roiFile, delimiter=',')
        for row in rowFile:
            print row
            imgContrastname = row[0]
            print imgContrastname
            imgFilename = row[1]
            print imgFilename
            ycoord = int(float(row[2]))
            print ycoord
            xcoord = int(float(row[3]))
            print xcoord

            aFeature = [imgContrastname, imgFilename, ycoord, xcoord]

            dicomfile = os.path.join(mapfileDir,imgFilename)
            dicomImage = Read2DImage(dicomfile)
            subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

            subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

            # GLCM
            glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

            for GLCMAngle in GLCMAngleList:
                for featureName in haralick_labels[:-1]:
                    aFeature.append(glcmFeatures[GLCMAngle][featureName])

            featureWriter.writerow(aFeature)







