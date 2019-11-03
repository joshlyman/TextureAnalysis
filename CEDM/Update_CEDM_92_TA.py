# Add Kutosis and Skewness of raw features inside 92 textures

import csv
import fnmatch
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels
from pylab import *

import ROI_ShapeAnalysis_92
from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures
from scipy.stats import kurtosis
from scipy.stats import skew

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

rootDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/Marley Grant Data_0410/Marley Grant Data/'

outputDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/CEDM_Update/Update_results/notremove92/'
featuresOutFn = 'CEDM_92_TA_shape_features_LBP1.csv'


# recfilenum = 0


def genFeatures():
    # dualRescaleOption: whether use both lesion and normal ROI for grayscale normalization
    # If 'False', use only lesion image
    # default value is 'True'

    # Parameters and feature list of each algorithm
    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

    LBPRadius = 1
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP1_%02d' % x)
    LBPFeatureList.append('LBP1_Other')

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

    MeanStdLBfeaturelist = ['LargestBox_Mean','LargestBox_Std','LargestBox_Kurtosis','LargestBox_Skewness']
    featureTitle = featureTitle + MeanStdLBfeaturelist

    shapetitlelist = ['compactness','entropy', 'bending energy','ratio(min/max)']
    featureTitle = featureTitle + shapetitlelist

    # List all dicom files and generate features for each images
    # Feature results stored in separate csv files for each folder
    featuresCSVFn = os.path.join(outputDir, featuresOutFn)
    casefilenum = 0

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
            if casefile == 'M24 - M24':
                continue
            if casefile == 'M5 - M5':
                continue
            print '\n'
            print casefile
            casefilenum +=1

            patientid = casefile.split('-')[0]

            patientfolderpath = os.path.join(rootDir, casefile)

            for patientfolder in os.listdir(patientfolderpath):
                if patientfolder.startswith('.'):
                    continue
                if patientfolder.startswith('..'):
                    continue
                if fnmatch.fnmatch(patientfolder, '*Icon*'):
                    continue
                if fnmatch.fnmatch(patientfolder, '*roi*'):
                    continue

                Dfolderpath = os.path.join(patientfolderpath, patientfolder)

                for phasefolder in os.listdir(Dfolderpath):

                    phasefolderpath = os.path.join(Dfolderpath, phasefolder)
                    if phasefolder.startswith('.'):
                        continue
                    if phasefolder.startswith('..'):
                        continue
                    if phasefolder.startswith('*Icon*'):
                        continue
                    if os.path.isfile(phasefolderpath):
                        continue

                    print phasefolder

                    phase1 = phasefolder.split('-')[0].replace(' ','')
                    if fnmatch.fnmatch(phase1,'*CC*DES*'):
                        phasename = 'CC DES'
                    elif fnmatch.fnmatch(phase1,'*CC*LE*'):
                        phasename = 'CC LE'
                    elif fnmatch.fnmatch(phase1, '*MLO*DES*'):
                        phasename = 'MLO DES'
                    elif fnmatch.fnmatch(phase1,'*MLO*LE*'):
                        phasename = 'MLO LE'
                    elif fnmatch.fnmatch(phase1, '*LM*DES*'):
                        phasename = 'LM DES'
                    else:
                        phasename = 'LM LE'

                    rectfile =''
                    contourfile = ''
                    dicomfile = ''
                    for file in os.listdir(phasefolderpath):

                        if fnmatch.fnmatch(file,'*texture*'):
                            continue
                        if fnmatch.fnmatch(file,'*(1)*'):
                            continue
                        if fnmatch.fnmatch(file,'*largest_rec*'):
                            rectfile= file


                        if fnmatch.fnmatch(file,'*csv*') or fnmatch.fnmatch(file,'*csv*'):
                            if not fnmatch.fnmatch(file,'*largest_rec*'):
                                contourfile = file

                        if fnmatch.fnmatch(file,'*dcm*'):
                            dicomfile = file

                    #print rectfile,contourfile,dicomfile

                    recpath = os.path.join(phasefolderpath,rectfile)
                    contourpath = os.path.join(phasefolderpath,contourfile)
                    dicompath = os.path.join(phasefolderpath,dicomfile)

                    shapedescriptors = ROI_ShapeAnalysis_92.genShapefeatures(contourpath)

                    with open(recpath, 'r') as roiFile:
                        roiList = csv.DictReader(roiFile, dialect='excel')
                        for aROI in roiList:
                            if (int(aROI['Y']) == 1) and (int(aROI['X']) == 1):
                                print('Invalid ROI for %s @ %s.' % (patientid, phasename))
                                continue

                            xcoord = int(aROI['X'])
                            ycoord = int(aROI['Y'])
                            width = int(aROI['W'])
                            height = int(aROI['H'])

                            dicomImage = Read2DImage(dicompath)
                            subImage = dicomImage[ycoord:(ycoord + height),
                                       xcoord:(xcoord + width)]  # errors here: before: Y + W

                            subImageLBP = dicomImage[ycoord - LBPRadius:(ycoord + height) + LBPRadius,
                                          xcoord - LBPRadius:(xcoord + width) + LBPRadius]

                            mean_LargBox = numpy.mean(subImage)
                            std_LargBox = numpy.std(subImage)

                            # add Skewness and Kurtosis in largest box here
                            SubImagelist = list()
                            SubImageArraylist = subImage.tolist()
                            for smalllist in SubImageArraylist:
                                SubImagelist += smalllist

                            Kurtosis_LargBox = kurtosis(SubImagelist)
                            Skewness_LargBox = skew(SubImagelist)

                            subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

                            extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImage.max(), subImage.min())

                            if numpy.all(subImage == 0):
                                print('%s @ %s is all zero.' % (patientid, phasename))
                                continue

                            aFeature = [patientid, phasename, aROI['Y'], aROI['X'], aROI['W'], aROI['H']]

                            # GLCM
                            # dont need to extended ROI
                            glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

                            for GLCMAngle in GLCMAngleList:
                                for featureName in haralick_labels[:-1]:
                                    aFeature.append(glcmFeatures[GLCMAngle][featureName])

                            # LBP
                            # need to use extended ROI
                            lbpFeatures = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius,
                                                                         LBPMethod)
                            aFeature = aFeature + lbpFeatures.tolist()

                            # Gabor
                            GaborFeatures = ExtendGaborFeatures.calcFeatures(dicomImage, xcoord, ycoord, width, height,
                                                                             Gaborkernel_bank, subImage.max(),
                                                                             subImage.min())
                            for gaborfeature in GaborFeatures:
                                aFeature = aFeature + gaborfeature.tolist()

                            aFeature = aFeature + [mean_LargBox, std_LargBox,Kurtosis_LargBox,Skewness_LargBox]

                            aFeature = aFeature + shapedescriptors

                            featureWriter.writerow(aFeature)



genFeatures()