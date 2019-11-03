# Version 4: can select features from single patient

import csv
import fnmatch
import os

import SimpleITK
import numpy

from mahotas.features.texture import haralick_labels
import GLCM_GUI
import ExtendGaborFeatures_GUI
import ExtendLBP_GUI

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

# rootDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/Marley Grant Data_0410/CEDM pilot data-selected/malignant'

# outputDir = '/Users/yanzhexu/Desktop/Research/TA GUI/CEDM/'

# featuresOutFn = 'CEDM_51_TA_malignant_features.csv'

def genTAfeatures(patientID,phasename,lesionDicom,lesionROIRectFn,GLCMdist,LBPrad,GLCM,LBP,GABOR,RAW,Gaborkernel_bank):

    with open(lesionROIRectFn, 'r') as roiFile:
        roiList = csv.DictReader(roiFile, dialect='excel')
        for aROI in roiList:
            if (int(aROI['Y']) == 1) and (int(aROI['X']) == 1):
                print('Invalid ROI for %s @ %s.' % (patientID, phasename))
                continue

            dicomImage = Read2DImage(lesionDicom)

            # in Python, coords should be coords(matlab)-1
            # coordinates from Osirtx: 0,0 so keep it not -1
            xcoord = int(aROI['X'])
            ycoord = int(aROI['Y'])
            width = int(aROI['W'])
            height = int(aROI['H'])

            subImage = dicomImage[ycoord:(ycoord + height), xcoord:(xcoord + width)]

            if numpy.all(subImage == 0):
                print('%s @ %s is all zero.' % (patientID, phasename))
                continue

            aFeature = [patientID, phasename, aROI['Y'], aROI['X'], aROI['W'], aROI['H']]

            # GLCM
            if GLCM == True:
                GLCMAngleList = ['0', '45', '90', '135', 'Avg']
                subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())
                glcmFeatures = GLCM_GUI.calcFeatures(subImageGLCM,GLCMdist)
                for GLCMAngle in GLCMAngleList:
                    for featureName in haralick_labels[:-1]:
                        aFeature.append(glcmFeatures[GLCMAngle][featureName])

            # LBP
            if LBP == True:
                LBPRadius = LBPrad
                LBPnPoints = 8 * LBPRadius
                LBPMethod = 'uniform'
                subImageLBP = dicomImage[ycoord - LBPRadius:(ycoord + height) + LBPRadius,
                              xcoord - LBPRadius:(xcoord + width) + LBPRadius]

                # for extended LBP, we still use grayscale range of 8*8 box to normalize extended ROI 10*10 box
                extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImage.max(), subImage.min())

                # need to use extended ROI
                lbpFeatures = ExtendLBP_GUI.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius, LBPMethod)
                aFeature = aFeature + lbpFeatures.tolist()

            # Gabor
            if GABOR == True:
                GaborFeatures = ExtendGaborFeatures_GUI.calcFeatures(dicomImage, xcoord, ycoord, width, height,
                                                             Gaborkernel_bank, subImage.max(), subImage.min())
                for gaborfeature in GaborFeatures:
                    aFeature = aFeature + gaborfeature.tolist()

            if RAW == True:
                ## get mean and standard deviation of lesion ROI's gray level of lagest box directly from subImage
                mean_LargBox = numpy.mean(subImage)
                std_LargBox = numpy.std(subImage)
                aFeature = aFeature + [mean_LargBox, std_LargBox]

            print aFeature
            return aFeature


def genFeatures(rootDir,outputDir,featuresOutFn,phasename,patient,GLCMdist,LBPrad,GLCM,LBP,GABOR,RAW):
    # Parameters and feature list of each algorithm

    # Generate full list of features combined with parameters
    featureTitle = ['PatientID', 'Phase', 'ROI_Y', 'ROI_X', 'Width', 'Height']

    if GLCM == True:
        GLCMAngleList = ['0', '45', '90', '135', 'Avg']
        for GLCMAngle in GLCMAngleList:
            for featureName in haralick_labels[:-1]:
                featureTitle.append(featureName + '_' + GLCMAngle)

    if LBP == True:
        LBPRadius = LBPrad
        LBPnPoints = 8 * LBPRadius
        LBPMethod = 'uniform'

        LBPFeatureList = []
        for x in xrange(0, LBPnPoints + 1):
            LBPFeatureList.append('LBP_%02d' % x)
        LBPFeatureList.append('LBP_Other')

        featureTitle = featureTitle + LBPFeatureList

    Gaborkernel_bank = []

    if GABOR == True:
        Gaborsigma_range = (1.0, 2.0)
        Gaborfreq_range = (0.1, 0.3, 0.5)
        kernel_bank = []
        Gaborkernel_bank = ExtendGaborFeatures_GUI.genKernelBank(Gaborsigma_range, Gaborfreq_range, kernel_bank)

        GaborFeatureList = ['Gabor_Mean', 'Gabor_Std']

        for GaborSigma in Gaborsigma_range:
            for GaborFreq in Gaborfreq_range:
                for featureName in GaborFeatureList:
                    featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    if RAW == True:
        MeanStdLBfeaturelist = ['LargestBox_Mean', 'LargestBox_Std']
        featureTitle = featureTitle + MeanStdLBfeaturelist

    print featureTitle
    print patient

    featuresCSVFn = os.path.join(outputDir, featuresOutFn)
    with open(featuresCSVFn, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')
        featureWriter.writerow(featureTitle)

        lesionDicom = patient + '.dcm'
        lesionCoord = patient + '.csv'

        lesionPath = os.path.join(rootDir, phasename)

        lesionDicomfile = os.path.join(lesionPath,lesionDicom)

        lesionCoordfile = os.path.join(lesionPath,lesionCoord)

        TAfeatures = genTAfeatures(patient,phasename,lesionDicomfile,lesionCoordfile,GLCMdist,LBPrad,GLCM,LBP,GABOR,RAW,Gaborkernel_bank)


        aFeature = TAfeatures
        featureWriter.writerow(aFeature)

    # print casenum
    print('Done.')


# parameter:
# 1. rootDir: input path after user browser dataset
# 2. phasename: modality: DES-CC, LE-CC, DES-MLO, LE-MLO, after user selects, it is decided
# 3. patient: user click select patients
# 4. GLCMdist: GLCM distance
# 5. LBPrad: LBP radius
# 6. phasename: modality: DES-CC, LE-CC, DES-MLO, LE-MLO
# 7. GLCM, LBP, GABOR, RAW: add/delete 4 features: True/False
rootDir = '/Users/yanzhexu/Desktop/Research/TA GUI/CEDM/Batchtest/Benign/'
outputDir = '/Users/yanzhexu/Desktop/Research/TA GUI/CEDM/Batchtest/'
featuresOutFn = 'CEDM_51_individualtest_features.csv'


genFeatures(rootDir,outputDir,featuresOutFn,phasename = 'DES-CC',patient='Pt1',GLCMdist=1,LBPrad=1,GLCM=True,LBP=True,GABOR=True,RAW=True)

