# original version

import csv
import fnmatch
import os

import SimpleITK
import numpy

from mahotas.features.texture import haralick_labels
import GLCM_GUI

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
rootDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/Marley Grant Data_0410/CEDM pilot data-selected/malignant'

outputDir = '/Users/yanzhexu/Desktop/Research/TA GUI/CEDM/'

featuresOutFn = 'CEDM_51_TA_malignant_features.csv'

def genTAfeatures(patientID,phasename,lesionDicom,lesionROIRectFn,GLCMdist):

    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

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

            subImageGLCM = GrayScaleNormalization(subImage,subImage.max(),subImage.min())

            if numpy.all(subImage == 0):
                print('%s @ %s is all zero.' % (patientID, phasename))
                continue

            aFeature = [patientID, phasename, aROI['Y'], aROI['X'], aROI['W'], aROI['H']]

            # GLCM

            glcmFeatures = GLCM_GUI.calcFeatures(subImageGLCM,GLCMdist)

            for GLCMAngle in GLCMAngleList:
                for featureName in haralick_labels[:-1]:
                    aFeature.append(glcmFeatures[GLCMAngle][featureName])

            # LBP



            # Gabor



            return aFeature

def removeduplcase(casefile,lesionfile):
    if casefile == 'Pt24':
        if fnmatch.fnmatch(lesionfile,'*LA__LCC_image_largest_rec*'):
            return False
        if fnmatch.fnmatch(lesionfile,'*LA__LCC*'):
            return False
    if casefile == 'Pt45':
        if fnmatch.fnmatch(lesionfile,'*DDL_LMLO2_image_largest_rec*'):
            return False
        if fnmatch.fnmatch(lesionfile,'*DDL_LMLO2*'):
            return False

    if casefile == 'Pt48':
        if fnmatch.fnmatch(lesionfile,'*GSA_RCC2_image_largest_rec*'):
            return False
        if fnmatch.fnmatch(lesionfile,'*GSA_RCC2*'):
            return False
        if fnmatch.fnmatch(lesionfile,'*GSA_RMLO2_image_largest_rec*'):
            return False
        if fnmatch.fnmatch(lesionfile,'*GSA_RMLO2*'):
            return False


def genFeatures(GLCMdist,phasename):
    # Parameters and feature list of each algorithm
    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

    # Generate full list of features combined with parameters
    featureTitle = ['PatientID', 'Phase', 'ROI_Y', 'ROI_X', 'Width', 'Height']

    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    # List all dicom files and generate features for each images
    # Feature results stored in separate csv files for each folder
    featuresCSVFn = os.path.join(outputDir, featuresOutFn)
    with open(featuresCSVFn, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')
        featureWriter.writerow(featureTitle)

        casenum = 0

        for casefile in os.listdir(rootDir):
            if casefile.startswith('.'):
                continue
            if casefile.startswith('..'):
                continue
            if fnmatch.fnmatch(casefile, '*Icon*'):
                continue

            casenum += 1

            print casefile

            roiCCFn = list()
            roiMLOFn = list()
            contourCCFn = list()
            contourMLOFn = list()
            roiDicomfile = dict()

            filename2 = os.path.join(rootDir, casefile)
            for lesionfile in os.listdir(filename2):
                if lesionfile.startswith('.'):
                    continue
                if lesionfile.startswith('..'):
                    continue
                if fnmatch.fnmatch(lesionfile, '*Icon*'):
                    continue
                if fnmatch.fnmatch(lesionfile, '*texture*'):
                    continue
                if fnmatch.fnmatch(lesionfile, '*CC*csv'):
                    if fnmatch.fnmatch(lesionfile, '*CC*largest_rec*csv'):

                        # filter Pt24, Pt45 and Pt48.
                        if removeduplcase(casefile,lesionfile) == False:
                            continue

                        roiCCFn.append(lesionfile)
                    else:
                        # filter Pt24, Pt45 and Pt48.
                        if removeduplcase(casefile, lesionfile) == False:
                            continue

                        contourCCFn.append(lesionfile)

                if fnmatch.fnmatch(lesionfile, '*MLO*csv'):
                    if fnmatch.fnmatch(lesionfile, '*MLO*largest_rec*csv'):
                        # filter Pt24, Pt45 and Pt48.
                        if removeduplcase(casefile, lesionfile) == False:
                            continue

                        roiMLOFn.append(lesionfile)
                    else:
                        # filter Pt24, Pt45 and Pt48.
                        if removeduplcase(casefile, lesionfile) == False:
                            continue

                        contourMLOFn.append(lesionfile)

                if fnmatch.fnmatch(lesionfile, '*DES*CC*dcm'):
                    roiDicomfile['DES-CC'] = lesionfile


                if fnmatch.fnmatch(lesionfile, '*LE*CC*dcm'):
                    roiDicomfile['LE-CC'] = lesionfile


                if fnmatch.fnmatch(lesionfile, '*DES*MLO*dcm'):
                    roiDicomfile['DES-MLO'] = lesionfile

                if fnmatch.fnmatch(lesionfile, '*LE*MLO*dcm'):
                    roiDicomfile['LE-MLO'] = lesionfile

            lesionPath = os.path.join(rootDir, casefile)

            patientID = casefile

            phasenames = [phasename]
            #phasenames =['DES-CC','LE-CC','DES-MLO','LE-MLO']

            for phasename in phasenames:

                lesionDicomFn = roiDicomfile[phasename]

                # DICOM file name with absolute path
                lesionDicom = os.path.join(lesionPath, lesionDicomFn)

                if fnmatch.fnmatch(phasename,'*CC'):

                    roiFn = roiCCFn[0]

                    # Largest rectangle file name with absolute path
                    lesionROIRectFn = os.path.join(lesionPath, roiFn)

                    TAfeatures = genTAfeatures(patientID,phasename,lesionDicom,lesionROIRectFn,GLCMdist)

                    if TAfeatures == None:
                        continue

                    aFeature = TAfeatures
                    featureWriter.writerow(aFeature)

                else:

                    roiFn = roiMLOFn[0]

                    # Largest rectangle file name with absolute path
                    lesionROIRectFn = os.path.join(lesionPath, roiFn)

                    TAfeatures = genTAfeatures(patientID,phasename,lesionDicom,lesionROIRectFn,GLCMdist)

                    if TAfeatures == None:
                        continue

                    aFeature = TAfeatures
                    featureWriter.writerow(aFeature)
    print casenum
    print('Done.')


# parameter:
# 1. GLCMdist: GLCM distance
# 2. phasename: modality: DES-CC, LE-CC, DES-MLO, LE-MLO

genFeatures(GLCMdist=1,phasename='DES-CC')