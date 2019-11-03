# Add Kutosis and Skewness of raw features inside 51 textures

import csv
import fnmatch
import os

import SimpleITK
import numpy

#from Mahotas.mahotas.features.texture import haralick_labels
from mahotas.features.texture import haralick_labels

import ROI_ShapeAnalysis_51
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


# Image Root Dir
rootDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/Marley Grant Data_0410/CEDM pilot data-selected/benign'

outputDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/CEDM_Update/Update_results/Update51'

# featuresOutFn = 'CEDM_51_TA_shape_malignant_features_LBP3.csv'
#featuresOutFn = 'CEDM_51_TA_shape_malignant_featuress.csv'
#featuresOutFn = 'CEDM_51_TA_shape_malignant_features.csv'
featuresOutFn = 'CEDM_51_TA_shape_benign_features_LBP3.csv'

def genTAfeatures(patientID,phasename,lesionDicom,lesionROIRectFn,Gaborkernel_bank):
    GLCMAngleList = ['0', '45', '90', '135', 'Avg']

    LBPRadius = 3 # To do: Change here
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

            subImageLBP = dicomImage[ycoord-LBPRadius:(ycoord + height)+LBPRadius, xcoord-LBPRadius:(xcoord + width) +LBPRadius]

            ## get mean and standard deviation of lesion ROI's gray level of lagest box directly from subImage
            mean_LargBox = numpy.mean(subImage)
            std_LargBox = numpy.std(subImage)


            # add Skewness and Kurtosis in largest box here
            SubImagelist = list()
            SubImageArraylist = subImage.tolist()
            for smalllist in SubImageArraylist:
                SubImagelist += smalllist

            Kurtosis_LargBox = kurtosis(SubImagelist)
            Skewness_LargBox = skew(SubImagelist)


            subImageGLCM = GrayScaleNormalization(subImage,subImage.max(),subImage.min())


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

            aFeature = aFeature + [mean_LargBox,std_LargBox,Kurtosis_LargBox,Skewness_LargBox]

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


def genFeatures():
    # Parameters and feature list of each algorithm
    GLCMAngleList = ['0', '45', '90', '135', 'Avg']
    #GLCMAngleList = ['Avg']


    LBPRadius = 3 # To do: change here
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP3_%02d' % x) # To do: change here
    LBPFeatureList.append('LBP3_Other')

    Gaborsigma_range = (1.0, 2.0) # To do: change here
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
            roiCoords = dict()
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

            phasenames =['DES-CC','LE-CC','DES-MLO','LE-MLO']

            for phasename in phasenames:
                #roiCoordsFn = roiCoords[phasename]
                lesionDicomFn = roiDicomfile[phasename]

                # DICOM file name with absolute path
                lesionDicom = os.path.join(lesionPath, lesionDicomFn)

                if fnmatch.fnmatch(phasename,'*CC'):

                    roiFn = roiCCFn[0]
                    contourFn = contourCCFn[0]

                    # Largest rectangle file name with absolute path
                    lesionROIRectFn = os.path.join(lesionPath, roiFn)

                    # contour data file name with absolute path
                    contourfilepath = os.path.join(lesionPath,contourFn)
                    shapedescriptors = ROI_ShapeAnalysis_51.genShapefeatures(contourfilepath)

                    TAfeatures = genTAfeatures(patientID,phasename,lesionDicom,lesionROIRectFn,Gaborkernel_bank)
                    #

                    if TAfeatures == None:
                        continue

                    aFeature = TAfeatures +shapedescriptors
                    featureWriter.writerow(aFeature)

                else:

                    roiFn = roiMLOFn[0]
                    contourFn = contourMLOFn[0]

                    # Largest rectangle file name with absolute path
                    lesionROIRectFn = os.path.join(lesionPath, roiFn)

                    # contour data file name with absolute path
                    contourfilepath = os.path.join(lesionPath,contourFn)
                    shapedescriptors = ROI_ShapeAnalysis_51.genShapefeatures(contourfilepath)

                    TAfeatures = genTAfeatures(patientID,phasename,lesionDicom,lesionROIRectFn,Gaborkernel_bank)

                    if TAfeatures == None:
                        continue

                    aFeature = TAfeatures +shapedescriptors
                    featureWriter.writerow(aFeature)
    print casenum
    print('Done.')


genFeatures()