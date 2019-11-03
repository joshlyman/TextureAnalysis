# 2nd version: GBM sliding window for all 6 contrast images and also

# do T2 sliding windows: Label windows which are also belong to T1 windows

# Recently update 0821: change the raw mean setting from 8*8 box normalization
# to raw feature w/o any normalization

# add PI and Necrosis are in another files: Add_PI_GBMSlidingwindow.py and Add_PI_Necro_GBMSlidingwindow.py

import csv
import os
import xml.etree.ElementTree as ET
import fnmatch
import numpy
import math
import SimpleITK
from mahotas.features.texture import haralick_labels


from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures

from GBM import GBMslidingWindowBoxMappingCoordinate

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'

coorDir = '/Users/yanzhexu/Desktop/Research/GBM/18/patient_biopsy_coordinates_18.csv'

mapDir = '/Users/yanzhexu/Desktop/Research/GBM/18/map between pt numbers and pt label letters.txt'

outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addYlabel/GBM_SlidingWindow_TextureMap'


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
# biopsy: 3 conditions: 1. in boundary 2. off boundary but in rectangle box 3. off boundary and out of box
def T2chooseinoutcoord(contourx1,contourx2,contoury1,contoury2,T1xycoord,T2xycoord,biopsycoordinatelist):

    print biopsycoordinatelist
    windowptlist = list()

    # for each point inside rectangle plot, check if each point inside boundary or outside boundary, inside: True, outside: False
    for testx in range(contourx1,contourx2+1):
        for testy in range(contoury1,contoury2+1):

            # check if point is inside T2 boundary or not
            T2inorout = point_inside_polygon(testx, testy, T2xycoord)

            if T2inorout == True:

                # check if point is inside T1 boundary or not
                T1inorout = point_inside_polygon(testx, testy, T1xycoord)

                windowptlist.append(list())
                windowptlist[len(windowptlist)-1].append(testx)
                windowptlist[len(windowptlist)-1].append(testy)

                # False means in boundary, window is boundary window, 1: center pt of boundary window, 0: not boundary, inside boundary pt
                if checkboxinout(testx,testy,T2xycoord) == False:
                    windowptlist[len(windowptlist) - 1].append(1)
                else:
                    windowptlist[len(windowptlist) - 1].append(0)

                # 1: biopsy pt (inside), 0: not biopsy pt (inside)
                if [testx,testy] in biopsycoordinatelist:
                    # remove from biopsy list
                    biopsycoordinatelist.remove([testx, testy])
                    windowptlist[len(windowptlist) - 1].append(1)
                else:
                    windowptlist[len(windowptlist) - 1].append(0)

                # 1: this window is also T1 window, 0: not belong to T1
                if T1inorout == True:
                    windowptlist[len(windowptlist)-1].append(1)
                else:
                    windowptlist[len(windowptlist)-1].append(0)

            # if point is off boundary and in rectangle box, but in biopsy, then add this pt, and add 2: off boundary pt, and 1: biopsy pt, and 1: T1 window center pt
            elif [testx, testy] in biopsycoordinatelist:

                print 'biopsy in rectangle box:',[testx,testy]

                # if out of boundary but in rectangle box
                biopsycoordinatelist.remove([testx,testy])

                T1inorout = point_inside_polygon(testx, testy, T1xycoord)

                windowptlist.append(list())
                windowptlist[len(windowptlist) - 1].append(testx)
                windowptlist[len(windowptlist) - 1].append(testy)

                windowptlist[len(windowptlist) - 1].append(2)
                windowptlist[len(windowptlist) - 1].append(1)

                # 1: this window is also T1 window, 0: not belong to T1
                if T1inorout == True:
                    windowptlist[len(windowptlist) - 1].append(1)
                else:
                    windowptlist[len(windowptlist) - 1].append(0)

    # if point is off boundary and out of rectangle box, add them all
    if len(biopsycoordinatelist)!=0:
        print 'rest biopsy:',biopsycoordinatelist
        for biopsyclist in biopsycoordinatelist:
            testx = biopsyclist[0]
            testy = biopsyclist[1]

            print 'biopsy out of rectangle box:', biopsyclist

            T1inorout = point_inside_polygon(testx, testy, T1xycoord)

            windowptlist.append(list())
            windowptlist[len(windowptlist) - 1].append(testx)
            windowptlist[len(windowptlist) - 1].append(testy)

            windowptlist[len(windowptlist) - 1].append(2)
            windowptlist[len(windowptlist) - 1].append(1)

            # 1: this window is also T1 window, 0: not belong to T1
            if T1inorout == True:
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


# get biopsy coordinates
biopsycoordinatefile = GBMslidingWindowBoxMappingCoordinate.getCoordinatefiles(mapDir, coorDir)


def genTextures():

    GLCMAngleList = ['Avg']
    featureTitle = ['Image Contrast', 'Image Filename','X', 'Y', 'Boundary (1) or not (inside: 0), (outside:2)', 'Biopsy(1) or not (0)','T1 window in T2 (1) or not (0)']

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
    Ylabel = ['Ylabel']

    featureTitle = featureTitle + MeanStdfeaturelist + Ylabel

    dicomnames = ['EPI', 'P', 'Q', 'RCBV', 'SPGRC', 'T2']

    for texturemapfile in os.listdir(rootDir):

        if texturemapfile.startswith('.'):
            continue
        if texturemapfile.startswith('..'):
            continue

        print texturemapfile

        patientname = texturemapfile.split('_')[0]
        if fnmatch.fnmatch(patientname, "*FSL*"):
            newpatientname = patientname.replace("FSL", "")
        elif fnmatch.fnmatch(patientname, "*h*"):
            newpatientname = patientname.replace("h", "")
        else:
            newpatientname = patientname
        print newpatientname

        slicepathfile = os.path.join(rootDir, texturemapfile)

        for slicefile in os.listdir(slicepathfile):
            if slicefile.startswith('.'):
                continue
            if slicefile.startswith('..'):
                continue

            print slicefile

            slicenum = slicefile.replace('slice', '')
            slicenum = int(slicenum)

            dcmxmlfilepath = os.path.join(slicepathfile, slicefile)

            dcmfiledict = dict()
            for dcmfile in os.listdir(dcmxmlfilepath):

                if dcmfile.startswith('.'):
                    continue
                if fnmatch.fnmatch(dcmfile, '*dcm*') is False:
                    continue
                if fnmatch.fnmatch(dcmfile, '*precontrast*'):
                    continue

                if fnmatch.fnmatch(dcmfile, '*C*SPGR*') or fnmatch.fnmatch(dcmfile, '*+C*T1*') or fnmatch.fnmatch(dcmfile,'*T1*+C*'):
                    SPGRCfile = dcmfile
                    dcmfiledict['SPGRC'] = SPGRCfile

                if fnmatch.fnmatch(dcmfile, '*T2*'):
                    T2file = dcmfile
                    dcmfiledict['T2'] = T2file

                if fnmatch.fnmatch(dcmfile, '*q*'):
                    Qfile = dcmfile
                    dcmfiledict['Q'] = Qfile

                if fnmatch.fnmatch(dcmfile, '*p*'):
                    Pfile = dcmfile
                    dcmfiledict['P'] = Pfile

                if fnmatch.fnmatch(dcmfile, '*rCBV*'):
                    RCBVfile = dcmfile
                    dcmfiledict['RCBV'] = RCBVfile

                if fnmatch.fnmatch(dcmfile, '*EPI*+C*') or fnmatch.fnmatch(dcmfile, '*+C*EPI*'):
                    EPIfile = dcmfile
                    dcmfiledict['EPI'] = EPIfile


            for xmlfile in os.listdir(dcmxmlfilepath):
                if not fnmatch.fnmatch(xmlfile, '*.xml'):
                    continue

                if fnmatch.fnmatch(xmlfile, '*NECROSIS*') or fnmatch.fnmatch(xmlfile,'*necrosis*'):
                    continue

                if fnmatch.fnmatch(xmlfile, '*C*SPGR*') or fnmatch.fnmatch(xmlfile, '*+C*T1*') or fnmatch.fnmatch(
                        xmlfile, '*T1*+C*'):
                    T1xmlfile = xmlfile

                if fnmatch.fnmatch(xmlfile, '*T2*'):
                    T2xmlfile = xmlfile


            print '\n'

            T1xmlfilepath = os.path.join(dcmxmlfilepath, T1xmlfile)
            T2xmlfilepath = os.path.join(dcmxmlfilepath, T2xmlfile)

            # only process those slice which has biopsy (CG slice 37 does not have biopsy so it does not have sliding window textures)
            if slicenum not in biopsycoordinatefile[newpatientname]:
                continue
            else:
                biopsycoordinatelist = biopsycoordinatefile[newpatientname][slicenum]

            T1xmin, T1xmax, T1ymin, T1ymax, T1xycoord = ParseXMLDrawROI(T1xmlfilepath)

            T2xmin, T2xmax, T2ymin, T2ymax, T2xycoord = ParseXMLDrawROI(T2xmlfilepath)

            # check if coords inside boundary or outside boundary
            T2windowptlist = T2chooseinoutcoord(T2xmin, T2xmax, T2ymin, T2ymax, T1xycoord, T2xycoord, biopsycoordinatelist)

            # start to do T1
            featuresOutFn = 'ROI_Texture_Map.csv'

            # start to do T2
            T2featuresOutFn = newpatientname + '_' + slicefile + '_' + 'T2' + '_' + featuresOutFn
            featuresCSVFn = os.path.join(outputDir, T2featuresOutFn)

            with open(featuresCSVFn, 'wb') as featureCSVFile:
                featureWriter = csv.writer(featureCSVFile, dialect='excel')
                featureWriter.writerow(featureTitle)

                for eachdcm in dicomnames:

                    print eachdcm
                    dicomfile = dcmfiledict[eachdcm]

                    dicomfilepath = os.path.join(dcmxmlfilepath, dicomfile)

                    dicomImage = Read2DImage(dicomfilepath)

                    for eachpt in T2windowptlist:

                        meanstd = list()
                        GLCM = list()
                        LBP = list()
                        Gabor = list()

                        xcoord = int(eachpt[0])
                        ycoord = int(eachpt[1])
                        boundaryornot = int(eachpt[2])
                        biopsyornot = int(eachpt[3])
                        T1ornot = int(eachpt[4])


                        aFeature = [eachdcm, dicomfile, xcoord, ycoord, boundaryornot, biopsyornot,T1ornot]

                        subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

                        subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

                        Raw_mean = numpy.mean(subImage)
                        Raw_std = numpy.std(subImage)

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

                        aFeature = aFeature + GLCM + LBP + Gabor + meanstd
                        featureWriter.writerow(aFeature)



genTextures()
