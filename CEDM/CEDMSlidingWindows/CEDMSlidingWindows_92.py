# Generate CEDM sliding window textures for 92 dataset

import csv
import fnmatch
import os
import math
import SimpleITK
import numpy
import xml.etree.ElementTree as ET

from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures


def Norm_Mean_Std_LargestBox(imgArray,imgMax,imgMin):

    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    meang = numpy.mean(imgArray)
    stdg = numpy.std(imgArray)

    return meang, stdg


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

# check if point is inside ROI boundary or outside boundary
def point_inside_polygon(x,y,poly):

    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside


# check if box covers part of boundary
def checkboxinout(testx, testy, xycoord):
    # check if box covers part of boundary
    b1 = point_inside_polygon(testx - 4, testy - 4, xycoord)
    b1h = point_inside_polygon(testx, testy - 4, xycoord)
    b2 = point_inside_polygon(testx - 4, testy + 4, xycoord)
    b2h = point_inside_polygon(testx - 4, testy, xycoord)
    b3 = point_inside_polygon(testx + 4, testy - 4, xycoord)
    b3h = point_inside_polygon(testx, testy + 4, xycoord)
    b4 = point_inside_polygon(testx + 4, testy + 4, xycoord)
    b4h = point_inside_polygon(testx + 4, testy, xycoord)

    if b1 != True or b1h != True or b2 != True or b2h != True or b3 != True or b3h != True or b4 != True or b4h != True:
        # False means one point of them is outside boundary, that means window is in boundary
        return False
    else:
        return True


# get points inside ROI
def chooseinoutcoord(contourx1,contourx2,contoury1,contoury2,xycoord):

    windowptlist = list()

    # for each point with interval 8 inside rectangle plot, check if each point inside boundary or outside boundary, inside: True, outside: False
    for testx in range(contourx1,contourx2+1,8):
        for testy in range(contoury1,contoury2+1,8):

            # check if point is inside boundary or not
            inorout = point_inside_polygon(testx, testy, xycoord)

            if inorout == True:

                windowptlist.append(list())
                windowptlist[len(windowptlist)-1].append(testx)
                windowptlist[len(windowptlist)-1].append(testy)

                # False means in boundary, window is boundary window, 1: center pt of boundary window, 0: not boundary, inside boundary pt
                if checkboxinout(testx,testy,xycoord) == False:
                    windowptlist[len(windowptlist) - 1].append(1)
                else:
                    windowptlist[len(windowptlist) - 1].append(0)

    return windowptlist


# process boundary points coordinate from XML file
def ParseXMLDrawROI(xmlfile):

    tree = ET.parse(xmlfile)
    root = tree.getroot()

    xcoordlist = list()
    ycoordlist = list()
    xycoordlist = list()

    for child in root.iter('string'):
        if not fnmatch.fnmatch(child.text,'*{*}*'):
            continue

        xcoords = str(child.text).split(',')[0]
        ycoords = str(child.text).split(',')[1]

        xc = float(xcoords.split('{')[1])
        yc = float(ycoords.split('}')[0].replace(' ',''))

        xcoordlist.append(xc)
        ycoordlist.append(yc)

        xycoordlist.append(list())
        xycoordlist[len(xycoordlist) - 1].append(xc)
        xycoordlist[len(xycoordlist) - 1].append(yc)

    xcoordlist.append(xcoordlist[0])
    ycoordlist.append(ycoordlist[0])

    # get x/y min/max in coords
    xmin = min(xcoordlist)
    ymin = min(ycoordlist)
    xmax = max(xcoordlist)
    ymax = max(ycoordlist)

    # ceil: get higher int
    # floor: get lower int
    xmin = int(math.floor(xmin))
    xmax = int(math.ceil(xmax))
    ymin = int(math.floor(ymin))
    ymax = int(math.ceil(ymax))

    return xmin,xmax,ymin,ymax,xycoordlist


def finddcmfile(phasefolderpath,xmlcasefolder,roiDicomfile,roiDicomfolder):

    print xmlcasefolder
    if fnmatch.fnmatch(xmlcasefolder, '*MLO*DES*'):
        for file in os.listdir(phasefolderpath):
            if fnmatch.fnmatch(file, '*dcm*'):
                roiDicomfolder['DES-MLO'] = xmlcasefolder
                roiDicomfile['DES-MLO'] = file
                print file
                # dcmnum +=1

    if fnmatch.fnmatch(xmlcasefolder, '*MLO*LE*'):
        for file in os.listdir(phasefolderpath):
            if fnmatch.fnmatch(file, '*dcm*'):
                roiDicomfolder['LE-MLO'] = xmlcasefolder
                roiDicomfile['LE-MLO'] = file
                print file
                # dcmnum +=1

    if fnmatch.fnmatch(xmlcasefolder, '*CC*DES*'):
        for file in os.listdir(phasefolderpath):
            if fnmatch.fnmatch(file, '*dcm*'):
                roiDicomfolder['DES-CC'] = xmlcasefolder
                roiDicomfile['DES-CC'] = file
                print file
                # dcmnum +=1

    if fnmatch.fnmatch(xmlcasefolder, '*CC*LE*'):
        for file in os.listdir(phasefolderpath):
            if fnmatch.fnmatch(file, '*dcm*'):
                roiDicomfolder['LE-CC'] = xmlcasefolder
                roiDicomfile['LE-CC'] = file
                print file
                # dcmnum +=1

    return roiDicomfile,roiDicomfolder


rootDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/Marley Grant Data'

outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box CEDM/addYlabel/raw92/'



def genFeatures():
    # Parameters and feature list of each algorithm
    GLCMAngleList = ['Avg']

    LBPRadius = 1
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

    LBPFeatureList = []
    for x in xrange(0, LBPnPoints + 1):
        LBPFeatureList.append('LBP_%02d' % x)
    LBPFeatureList.append('LBP_Other')

    Gaborsigma_range = (0.6, 1.0)
    Gaborfreq_range = (0.1, 0.3, 0.5)
    kernel_bank = []

    Gaborkernel_bank = ExtendGaborFeatures.genKernelBank(Gaborsigma_range, Gaborfreq_range, kernel_bank)

    GaborFeatureList = ['Gabor_Mean', 'Gabor_Std']

    # Generate full list of features combined with parameters
    featureTitle = ['PatientID', 'Dicom Image Filename', 'Xml Filename', 'Phase Name', 'X', 'Y', 'Boundary (1) or not (inside: 0)']

    for GLCMAngle in GLCMAngleList:
        for featureName in haralick_labels[:-1]:
            featureTitle.append(featureName + '_' + GLCMAngle)

    featureTitle = featureTitle + LBPFeatureList

    for GaborSigma in Gaborsigma_range:
        for GaborFreq in Gaborfreq_range:
            for featureName in GaborFeatureList:
                featureTitle.append(featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    MeanStdLBfeaturelist = ['Raw_Mean','Raw_Std']
    featureTitle = featureTitle + MeanStdLBfeaturelist + ['Ylabel']

    for eachptfolder in os.listdir(rootDir):
        if eachptfolder.startswith('.'):
            continue
        if eachptfolder.startswith('..'):
            continue
        if fnmatch.fnmatch(eachptfolder, '*Icon*'):
            continue
        if eachptfolder == 'M24 - M24':
            continue
        if eachptfolder == 'M5 - M5':
            continue


        # ptnum+=1
        print('\n')
        # print eachptfolder

        patientID = eachptfolder.split('-')[0]
        print patientID

        if fnmatch.fnmatch(eachptfolder,'*B*'):
            twofolder = 'benign'
        else:
            twofolder = 'malignant'

        rootDir2 = os.path.join(rootDir, eachptfolder)

        for folder2 in os.listdir(rootDir2):
            if folder2.startswith('.'):
                continue
            if folder2.startswith('..'):
                continue
            if fnmatch.fnmatch(folder2, '*Icon*'):
                continue
            if fnmatch.fnmatch(folder2,'*roi*'):
                continue

            # print folder2

            rootDir3 = os.path.join(rootDir2,folder2)

            ccxmlfile = list()
            mloxmlfile = list()
            roiDicomfile = dict()
            roiDicomfolder = dict()
            phasefolderpath =''

            for xmlcasefolder in os.listdir(rootDir3):
                phasefolderpath = os.path.join(rootDir3,xmlcasefolder)

                if xmlcasefolder.startswith('.'):
                    continue
                if xmlcasefolder.startswith('..'):
                    continue
                if fnmatch.fnmatch(xmlcasefolder, '*Icon*'):
                    continue

                if fnmatch.fnmatch(xmlcasefolder,'*CC*xml'):
                    ccxmlfile.append(xmlcasefolder)
                    print ccxmlfile
                    # xmlnum+=1

                if fnmatch.fnmatch(xmlcasefolder,'*MLO*xml'):
                    mloxmlfile.append(xmlcasefolder)
                    print mloxmlfile
                    # xmlnum+=1

                if os.path.isdir(phasefolderpath):

                    roiDicomfile,roiDicomfolder = finddcmfile(phasefolderpath,xmlcasefolder,roiDicomfile,roiDicomfolder)

            roiccxmlpath = os.path.join(rootDir3, ccxmlfile[0])
            roimloxmlpath = os.path.join(rootDir3, mloxmlfile[0])

            CCxmin, CCxmax, CCymin, CCymax, CCxycoord = ParseXMLDrawROI(roiccxmlpath)
            MLOxmin, MLOxmax, MLOymin, MLOymax, MLOxycoord = ParseXMLDrawROI(roimloxmlpath)

            # check if coords inside boundary or outside boundary
            CCwindowptlist = chooseinoutcoord(CCxmin, CCxmax, CCymin, CCymax, CCxycoord)
            MLOwindowptlist = chooseinoutcoord(MLOxmin, MLOxmax, MLOymin, MLOymax, MLOxycoord)

            featuresOutFn = 'ROI_Texture_Map.csv'

            # start to do T2
            featuresOutFn = patientID + '_' + twofolder + '_'+ featuresOutFn
            featuresCSVFn = os.path.join(outputDir, featuresOutFn)

            phasenames = ['DES-CC', 'LE-CC', 'DES-MLO', 'LE-MLO']

            with open(featuresCSVFn, 'wb') as featureCSVFile:
                featureWriter = csv.writer(featureCSVFile, dialect='excel')
                featureWriter.writerow(featureTitle)

                for phase in phasenames:

                    print phase
                    lesionDicomFn = roiDicomfile[phase]

                    lesionDicomFolder = roiDicomfolder[phase]

                    lesionDicomFolderpath = os.path.join(rootDir3,lesionDicomFolder)
                    dicomfilepath = os.path.join(lesionDicomFolderpath,lesionDicomFn)

                    dicomImage = Read2DImage(dicomfilepath)

                    if fnmatch.fnmatch(phase, '*CC'):

                        for eachpt in CCwindowptlist:

                            meanstd = list()
                            GLCM = list()
                            LBP = list()
                            Gabor = list()

                            xcoord = int(eachpt[0])
                            ycoord = int(eachpt[1])
                            boundaryornot = int(eachpt[2])

                            aFeature = [patientID, lesionDicomFn, ccxmlfile[0], phase, xcoord, ycoord, boundaryornot]

                            subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

                            subshape = numpy.shape(subImage)
                            if subshape[0] != 8 or subshape[1] != 8:
                                continue

                            subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

                            # get normalized to 0, 255: raw mean and standard deviation
                            Raw_mean, Raw_std = Norm_Mean_Std_LargestBox(subImage, subImage.max(), subImage.min())
                            meanstd.append(Raw_mean)
                            meanstd.append(Raw_std)

                            # GLCM
                            glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

                            for GLCMAngle in GLCMAngleList:
                                for featureName in haralick_labels[:-1]:
                                    GLCM.append(glcmFeatures[GLCMAngle][featureName])

                            # LBP subimage
                            subImageLBP = dicomImage[ycoord - 4 - LBPRadius:ycoord + 4 + LBPRadius,
                                          xcoord - 4 - LBPRadius: xcoord + 4 + LBPRadius]

                            extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImage.max(),
                                                                       subImage.min())

                            # need to use extended ROI
                            LBPs = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius,
                                                                  LBPMethod)
                            for lbp in LBPs:
                                LBP.append(lbp)

                            # Gabor, width = 8
                            # use extended ROI
                            GaborFeatures = ExtendGaborFeatures.calcFeatures(dicomImage, xcoord - 4, ycoord - 4,
                                                                             8, 8,
                                                                             Gaborkernel_bank, subImage.max(),
                                                                             subImage.min())

                            for gaborfeature in GaborFeatures:
                                for eachg in gaborfeature:
                                    Gabor.append(eachg)

                            TAfeatures = GLCM + LBP + Gabor + meanstd

                            if TAfeatures == None:
                                continue

                            aFeature = aFeature + TAfeatures
                            featureWriter.writerow(aFeature)

                    else:

                        for eachpt in MLOwindowptlist:

                            meanstd = list()
                            GLCM = list()
                            LBP = list()
                            Gabor = list()

                            xcoord = int(eachpt[0])
                            ycoord = int(eachpt[1])
                            boundaryornot = int(eachpt[2])

                            aFeature = [patientID, lesionDicomFn, mloxmlfile[0], phase, xcoord, ycoord, boundaryornot]

                            subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

                            subshape = numpy.shape(subImage)
                            # print subshape
                            # for some box, it is nearly boundary of image, like Pt36, it cannot generate 8*8 box
                            if subshape[0] != 8 or subshape[1] != 8:
                                continue

                            subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

                            # get normalized to 0, 255: raw mean and standard deviation
                            Raw_mean, Raw_std = Norm_Mean_Std_LargestBox(subImage, subImage.max(), subImage.min())
                            meanstd.append(Raw_mean)
                            meanstd.append(Raw_std)

                            # GLCM
                            glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

                            for GLCMAngle in GLCMAngleList:
                                for featureName in haralick_labels[:-1]:
                                    GLCM.append(glcmFeatures[GLCMAngle][featureName])

                            # LBP subimage
                            subImageLBP = dicomImage[ycoord - 4 - LBPRadius:ycoord + 4 + LBPRadius,
                                          xcoord - 4 - LBPRadius: xcoord + 4 + LBPRadius]

                            extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImage.max(),
                                                                       subImage.min())

                            # need to use extended ROI
                            LBPs = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius,
                                                                  LBPMethod)
                            for lbp in LBPs:
                                LBP.append(lbp)

                            # Gabor, width = 8
                            # use extended ROI
                            GaborFeatures = ExtendGaborFeatures.calcFeatures(dicomImage, xcoord - 4, ycoord - 4,
                                                                             8, 8,
                                                                             Gaborkernel_bank, subImage.max(),
                                                                             subImage.min())

                            for gaborfeature in GaborFeatures:
                                for eachg in gaborfeature:
                                    Gabor.append(eachg)

                            TAfeatures = GLCM + LBP + Gabor + meanstd

                            if TAfeatures == None:
                                continue

                            aFeature = aFeature + TAfeatures
                            featureWriter.writerow(aFeature)



genFeatures()


#
# print ptnum
# print xmlnum
# print dcmnum