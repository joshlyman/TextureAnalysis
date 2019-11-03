import csv
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels
from scipy.stats import kurtosis
from scipy.stats import skew

from GLCM import GLCMFeatures
from Gabor import MinACRExtendGaborFeatures
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

def MinMaxSubImageGen(subImage1,subImage2,subImage3,subImage4,height,width):
    # initilize min and max image matrix

    minImage = numpy.zeros((height, width))
    maxImage = numpy.zeros((height, width))

    # find min / max gray scale in each point of 4 subimage matrix
    for yi in range(height):
        for xi in range(width):
            gl1 = subImage1[yi, xi]
            gl2 = subImage2[yi, xi]
            gl3 = subImage3[yi, xi]
            gl4 = subImage4[yi, xi]

            mingl = min(gl1, gl2, gl3, gl4)
            maxgl = max(gl1, gl2, gl3, gl4)

            # put min / max gray scale in min / max image matrix
            minImage[yi, xi] = mingl
            maxImage[yi, xi] = maxgl

    return minImage,maxImage

rootDir = '/Users/yanzhexu/Desktop/Research/MinMax/ACR'

outputDir = '/Users/yanzhexu/Desktop/Research/MinMax/Final_results'

featuresOutFn = 'ACR_MinMap_features_LBP3.csv'
#featuresOutFn = 'ACR_MinMap_features_LBP3.csv'

timepointlist = ['time_1','time_2','time_3','time_4']
dicomfile = 'image.dcm'
largestboxfile = 'largest_rec.csv'


def genFeatures():
    # Parameters and feature list of each algorithm

    GLCMAngleList = ['Avg']

    LBPRadius = 3
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP_%02d' % x)
    LBPFeatureList.append('LBP_Other')

    Gaborsigma_range = (0.6, 1.0)
    Gaborfreq_range = (0.1, 0.3, 0.5)
    kernel_bank = []

    Gaborkernel_bank = MinACRExtendGaborFeatures.genKernelBank(Gaborsigma_range, Gaborfreq_range, kernel_bank)

    GaborFeatureList = ['Gabor_Mean', 'Gabor_Std', 'Gabor_Kurtosis', 'Gabor_Skewness']

    # Generate full list of features combined with parameters
    featureTitle = ['PatientID', 'ROI_Y', 'ROI_X', 'Width', 'Height']

    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    featureTitle = featureTitle + LBPFeatureList

    for GaborSigma in Gaborsigma_range:
        for GaborFreq in Gaborfreq_range:
            for featureName in GaborFeatureList:
                featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    MeanStdLBfeaturelist = ['LargestBox_Mean','LargestBox_Std','LargestBox_Kurtosis','LargestBox_Skewness']
    featureTitle = featureTitle + MeanStdLBfeaturelist

    # List all dicom files and generate features for each images
    # Feature results stored in separate csv files for each folder
    featuresCSVFn = os.path.join(outputDir, featuresOutFn)

    with open(featuresCSVFn, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')
        featureWriter.writerow(featureTitle)

        for ACRfolder in os.listdir(rootDir):
            if ACRfolder.startswith('.'):
                continue
            if ACRfolder.startswith('..'):
                continue

            patientid = ACRfolder.split('_')[0] + ACRfolder.split('_')[1]

            ACRpath = os.path.join(rootDir,ACRfolder)

            for lesionfolder in os.listdir(ACRpath):
                if lesionfolder.startswith('.'):
                    continue
                if lesionfolder.startswith('..'):
                    continue

                ACRlesionpath = os.path.join(ACRpath,lesionfolder)

                # get timepoint folder path
                timepointpath1 = os.path.join(ACRlesionpath, timepointlist[0])
                timepointpath2 = os.path.join(ACRlesionpath, timepointlist[1])
                timepointpath3 = os.path.join(ACRlesionpath, timepointlist[2])
                timepointpath4 = os.path.join(ACRlesionpath, timepointlist[3])

                # get lesion dicom file path
                lesionDicom1 = os.path.join(timepointpath1, dicomfile)
                lesionDicom2 = os.path.join(timepointpath2, dicomfile)
                lesionDicom3 = os.path.join(timepointpath3, dicomfile)
                lesionDicom4 = os.path.join(timepointpath4, dicomfile)

                # get image gray scale from each dicom file
                dicomImage1 = Read2DImage(lesionDicom1)
                dicomImage2 = Read2DImage(lesionDicom2)
                dicomImage3 = Read2DImage(lesionDicom3)
                dicomImage4 = Read2DImage(lesionDicom4)

                # get largest box coordinate
                lesionROIRectFn1 = os.path.join(timepointpath1, largestboxfile)
                lesionROIRectFn2 = os.path.join(timepointpath2, largestboxfile)
                lesionROIRectFn3 = os.path.join(timepointpath3, largestboxfile)
                lesionROIRectFn4 = os.path.join(timepointpath4, largestboxfile)

                # get subimage and subimage LBP from dicom image of 4 time points
                with open(lesionROIRectFn1, 'r') as roiFile:
                    roiList = csv.DictReader(roiFile, dialect='excel')
                    for aROI in roiList:
                        xcoord1 = int(aROI['X'])
                        ycoord1 = int(aROI['Y'])
                        width1 = int(aROI['W'])
                        height1 = int(aROI['H'])

                subImage1 = dicomImage1[ycoord1:ycoord1 + height1, xcoord1:xcoord1 + width1]

                subImageLBP1 = dicomImage1[ycoord1 - LBPRadius:(ycoord1 + height1) + LBPRadius, xcoord1 - LBPRadius:(xcoord1 + width1) + LBPRadius]

                with open(lesionROIRectFn2, 'r') as roiFile:
                    roiList = csv.DictReader(roiFile, dialect='excel')
                    for aROI in roiList:
                        xcoord2 = int(aROI['X'])
                        ycoord2 = int(aROI['Y'])
                        width2 = int(aROI['W'])
                        height2 = int(aROI['H'])

                subImage2 = dicomImage2[ycoord2:ycoord2 + height2, xcoord2:xcoord2 + width2]

                subImageLBP2 = dicomImage2[ycoord2 - LBPRadius:(ycoord2 + height2) + LBPRadius, xcoord2 - LBPRadius:(xcoord2 + width2) + LBPRadius]

                with open(lesionROIRectFn3, 'r') as roiFile:
                    roiList = csv.DictReader(roiFile, dialect='excel')
                    for aROI in roiList:
                        xcoord3 = int(aROI['X'])
                        ycoord3 = int(aROI['Y'])
                        width3 = int(aROI['W'])
                        height3 = int(aROI['H'])

                subImage3 = dicomImage3[ycoord3:ycoord3 + height3, xcoord3:xcoord3 + width3]

                subImageLBP3 = dicomImage3[ycoord3 - LBPRadius:(ycoord3 + height3) + LBPRadius, xcoord3 - LBPRadius:(xcoord3 + width3) + LBPRadius]

                with open(lesionROIRectFn4, 'r') as roiFile:
                    roiList = csv.DictReader(roiFile, dialect='excel')
                    for aROI in roiList:
                        xcoord4 = int(aROI['X'])
                        ycoord4 = int(aROI['Y'])
                        width4 = int(aROI['W'])
                        height4 = int(aROI['H'])

                subImage4 = dicomImage4[ycoord4:ycoord4 + height4, xcoord4:xcoord4 + width4]

                subImageLBP4 = dicomImage4[ycoord4 - LBPRadius:(ycoord4 + height4) + LBPRadius, xcoord4 - LBPRadius:(xcoord4 + width4) + LBPRadius]

                # generate min/max image matrix (same width and height in 4 matrix)
                MinSubImage,MaxSubImage = MinMaxSubImageGen(subImage1,subImage2,subImage3,subImage4,height1,width1)

                # minsize = numpy.shape(MinImage)
                # maxsize = numpy.shape(MaxImage)
                # print 'original:',minsize,maxsize

                # get extended LBP height, width
                LBPheight = height1 + 2*LBPRadius
                LBPwidth =  width1 + 2*LBPRadius

                # get min/ max LBP subimage from 4 LBP subimages
                MinLBPSubImage,MaxLBPSubImage = MinMaxSubImageGen(subImageLBP1,subImageLBP2,subImageLBP3,subImageLBP4, LBPheight,LBPwidth)

                # LBPminsize = numpy.shape(MinLBPImage)
                # LBPmaxsize = numpy.shape(MaxLBPImage)
                # print 'LBP:',LBPminsize,LBPmaxsize

                # get raw mean/ std from min subimage
                mean_LargBox = numpy.mean(MinSubImage)
                std_LargBox = numpy.std(MinSubImage)

                # add Kurtosis and Skewness into Raw Features
                MinSubImagelist = list()
                MinSubImageArraylist = MinSubImage.tolist()
                for smalllist in MinSubImageArraylist:
                    MinSubImagelist += smalllist

                Kurtosis_LargBox = kurtosis(MinSubImagelist)
                Skewness_LargBox = skew(MinSubImagelist)

                # normalized original subimage, GLCM can use this
                subImageGLCM = GrayScaleNormalization(MinSubImage, MinSubImage.max(), MinSubImage.min())
                # print subImageGLCM

                # for extended LBP, we still use grayscale range of 8*8 box to normalize extended ROI 10*10 box (LBP radius = 1)
                extendsubImageLBP = GrayScaleNormalization(MinLBPSubImage, MinSubImage.max(), MinSubImage.min())

                if numpy.all(MinSubImage == 0):
                    print('%s @ %s is all zero.' % (patientid))
                    continue

                aFeature = [patientid, ycoord1,xcoord1,width1,height1]

                # GLCM
                glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

                for GLCMAngle in GLCMAngleList:
                    for featureName in haralick_labels[:-1]:
                        aFeature.append(glcmFeatures[GLCMAngle][featureName])

                # LBP
                # need to use extended ROI
                lbpFeatures = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius, LBPMethod)
                aFeature = aFeature + lbpFeatures.tolist()

                # Gabor
                GaborFeatures = MinACRExtendGaborFeatures.calcFeatures(dicomImage1,dicomImage2,dicomImage3,dicomImage4, xcoord1, ycoord1, xcoord2,
                ycoord2,xcoord3,ycoord3,xcoord4,ycoord4, width1, height1, Gaborkernel_bank, MinSubImage.max(), MinSubImage.min())

                for gaborfeature in GaborFeatures:
                    aFeature = aFeature + gaborfeature.tolist()

                aFeature = aFeature + [mean_LargBox, std_LargBox,Kurtosis_LargBox,Skewness_LargBox]
                featureWriter.writerow(aFeature)


genFeatures()


