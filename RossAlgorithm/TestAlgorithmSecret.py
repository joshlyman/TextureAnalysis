#!/usr/bin/env python
#=========================================================================
#
# Extract texture features from a region-of-interest within a GBM dicom image
#
#
#=========================================================================

# log
#
# Test Dr. Ross Mitchell's algorithm on GBM data
# to find error on our code
#

import csv
import os

import matplotlib as mpl
import numpy as np

import GLCMTextureSecret
import TextureSecret

print mpl.get_cachedir()


# import SimpleITK as sitk
# from string import maketrans

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/RWh_slices_only/slice17/'

outputDir = '/Users/yanzhexu/Desktop/Research/GBM/TestGLCM'

featuresOutFn = 'GBM_features_GLCM_test_X_Y_ym4xm4_yp4xp4_TestAlgorithm.csv'

featureCSVFn = os.path.join(outputDir,featuresOutFn)

grayScales = 256

ycoord = 126
xcoord = 161

rootFnImg = os.path.join(rootDir,'EPI+C_IM-0003-0017.dcm')

inputImage = TextureSecret.readDicomImage(rootFnImg)


subImage = inputImage[ycoord - 4: ycoord + 4,xcoord - 4:xcoord + 4 ]

print subImage

print np.min(subImage)
print np.max(subImage)

subImage = TextureSecret.scaleIntensity(subImage, 0, grayScales)


subImage = np.rint(subImage).astype(np.uint8)



print subImage


features = GLCMTextureSecret.computeFeatures(subImage)

featureTitle = GLCMTextureSecret._getGLCMFeatureNames()

print featureTitle
print len(featureTitle)
print features
print len(features)

rowfeature = list()

for eachtitle in featureTitle:
    featurename = eachtitle +' Mean'
    rowfeature.append(features[featurename])

print rowfeature

with open(featureCSVFn, 'wb') as featureCSVFile:
    featureWriter = csv.writer(featureCSVFile, dialect='excel')
    featureWriter.writerow(featureTitle)

    featureWriter.writerow(rowfeature)


