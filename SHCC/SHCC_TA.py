import csv
import fnmatch
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures

rootDir = '/Users/yanzhexu/Desktop/Research/SHHCC_ROI_TIFF/'


outputDir = '/Users/yanzhexu/Desktop/Research/'

featuresOutFn = 'SHCC_lesion_features.csv'



def GrayScaleNormalization(imgArray, imgMax,imgMin):

    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    # transfer to closest int
    #imgArray = numpy.rint(imgArray).astype(numpy.uint8)
    imgArray = numpy.rint(imgArray).astype(numpy.int16)

    return imgArray


def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[:, :,1]

    if len(imgArray.shape) == 4:
        imgArray = imgArray[:,:,1]

    return imgArray


def genTAfeatures(patientID,phasename,lesionDicom,lesionROIRectFn,Gaborkernel_bank):
    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

    LBPRadius = 1
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

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

            subImage = dicomImage[ycoord:(ycoord + height), xcoord:(xcoord + width)] # errors here: before: Y + W

            # if patientID == 'SHHCC_2468':
            #     print xcoord
            #     print ycoord
            #
            #     print dicomImage
            #     print phasename
            #     print(subImage)
            #     print lesionDicom
            #     print lesionROIRectFn

            subImageLBP = dicomImage[ycoord-LBPRadius:(ycoord + height)+LBPRadius, xcoord-LBPRadius:(xcoord + width) +LBPRadius]

            ## get mean and standard deviation of lesion ROI's gray level of lagest box directly from subImage
            mean_LargBox = numpy.mean(subImage)
            std_LargBox = numpy.std(subImage)

            subImageGLCM = GrayScaleNormalization(subImage,subImage.max(),subImage.min())

            # if patientID == 'SHHCC_2468':
            #     print phasename
            #     print(subImageGLCM)
            #     print(numpy.shape(subImageGLCM))
            #     print(numpy.min(subImageGLCM))
            #     print (numpy.max(subImageGLCM))

            # for extended LBP, we still use grayscale range of 8*8 box to normalize extended ROI 10*10 box
            extendsubImageLBP = GrayScaleNormalization(subImageLBP,subImage.max(),subImage.min())

            if numpy.all(subImage == 0):
                print('%s @ %s is all zero.' % (patientID, phasename))
                continue

            aFeature = [patientID, phasename, aROI['Y'], aROI['X'], aROI['W'], aROI['H']]

            # GLCM
            # dont need to extended ROI
            glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

            for GLCMAngle in GLCMAngleList:
                for featureName in haralick_labels[:-1]:
                    aFeature.append(glcmFeatures[GLCMAngle][featureName])

            # LBP
            # need to use extended ROI
            lbpFeatures = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius, LBPMethod)
            aFeature = aFeature + lbpFeatures.tolist()

            # Gabor
            GaborFeatures = ExtendGaborFeatures.calcFeatures(dicomImage, xcoord, ycoord, width, height, Gaborkernel_bank, subImage.max(), subImage.min())

            for gaborfeature in GaborFeatures:

                aFeature = aFeature + gaborfeature.tolist()

            aFeature = aFeature + [mean_LargBox,std_LargBox]

            return aFeature




def genFeatures():

    GLCMAngleList = ['0', '45', '90', '135', 'Avg']
    #GLCMAngleList = ['Avg']


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
    featureTitle = ['PatientID', 'Phase', 'ROI_Y', 'ROI_X', 'Width', 'Height']

    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    featureTitle = featureTitle + LBPFeatureList

    for GaborSigma in Gaborsigma_range:
        for GaborFreq in Gaborfreq_range:
            for featureName in GaborFeatureList:
                featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    MeanStdLBfeaturelist = ['LargestBox_Mean','LargestBox_Std']
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

            # if fnmatch.fnmatch(casefile,'*2475*'):
            #     continue
            print casefile

            lesionPath = os.path.join(rootDir, casefile)

            patientID = casefile

            phasenames = ['Ph0', 'Ph1', 'Ph2', 'Ph3']

            for phasename in phasenames:
                # roiCoordsFn = roiCoords[phasename]
                # lesionDicomFn = roiDicomfile[phasename]

                lesionDicomFn = os.path.join(lesionPath,phasename)

                lesionROIRectFn = ''

                for lesionfolder in os.listdir(lesionDicomFn):
                    if fnmatch.fnmatch(lesionfolder,'*Lesion*'):
                        lesionfolderpath = os.path.join(lesionDicomFn,lesionfolder)

                        for csvfile in os.listdir(lesionfolderpath):
                            if fnmatch.fnmatch(csvfile,'*csv*'):
                                lesionROIRectFn = os.path.join(lesionfolderpath,csvfile)



                for lesionfile in os.listdir(lesionDicomFn):
                    if fnmatch.fnmatch(lesionfile,'*tiff*'):

                        # DICOM file name with absolute path
                        lesionDicom = os.path.join(lesionDicomFn,lesionfile)

                        print phasename
                        TAfeatures = genTAfeatures(patientID, phasename, lesionDicom, lesionROIRectFn,
                                                   Gaborkernel_bank)
                        #
                        # print (TAfeatures)


                        if TAfeatures == None:
                            continue
                        featureWriter.writerow(TAfeatures)


genFeatures()