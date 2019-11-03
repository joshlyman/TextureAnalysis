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

outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm/TextureMap_Results/'


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


# get points inside ROI
def chooseinoutcoord(contourx1,contourx2,contoury1,contoury2,xycoord,bcchecklist,biopsycoordinatelist):

    print biopsycoordinatelist
    windowptlist = list()
    # for each point inside rectangle plot, check if each point inside boundary or outside boundary, inside: True, outside: False
    for testx in range(contourx1,contourx2+1):
        for testy in range(contoury1,contoury2+1):

            # check if point is inside boundary or not
            inorout = point_inside_polygon(testx, testy, xycoord)

            if inorout == True:

                windowptlist.append(list())
                windowptlist[len(windowptlist)-1].append(testx)
                windowptlist[len(windowptlist)-1].append(testy)

                # 1: boundary pt, 0: not boundary, inside boundary pt
                if [testx,testy] in bcchecklist:
                    windowptlist[len(windowptlist) - 1].append(1)
                else:
                    windowptlist[len(windowptlist) - 1].append(0)

                # 1: biopsy pt (inside), 0: not biopsy pt (inside)
                if [testx,testy] in biopsycoordinatelist:
                    windowptlist[len(windowptlist) - 1].append(1)
                else:
                    windowptlist[len(windowptlist) - 1].append(0)

            # if point is off boundary but in biopsy, then add this pt, and add 2: off boundary pt and 1: biopsy pt
            elif [testx, testy] in biopsycoordinatelist:
                windowptlist.append(list())
                windowptlist[len(windowptlist) - 1].append(testx)
                windowptlist[len(windowptlist) - 1].append(testy)

                windowptlist[len(windowptlist) - 1].append(2)
                windowptlist[len(windowptlist) - 1].append(1)

    return windowptlist


# process boundary points coordinate from XML file
def ParseXMLDrawROI(xmlfile,biopsycoordinatelist):

    tree = ET.parse(xmlfile)
    root = tree.getroot()

    xcoordlist = list()
    ycoordlist = list()
    xycoordlist = list()

    bcchecklist = list()

    for child in root.iter('string'):
        if not fnmatch.fnmatch(child.text,'*{*}*'):
            continue

        xcoords = str(child.text).split(',')[0]
        ycoords = str(child.text).split(',')[1]

        xc = float(xcoords.split('{')[1])
        yc = float(ycoords.split('}')[0].replace(' ',''))

        checkxc = int(numpy.rint(xc))
        checkyc = int(numpy.rint(yc))

        xcoordlist.append(xc)
        ycoordlist.append(yc)

        xycoordlist.append(list())
        xycoordlist[len(xycoordlist) - 1].append(xc)
        xycoordlist[len(xycoordlist) - 1].append(yc)

        bcchecklist.append(list())
        bcchecklist[len(bcchecklist) - 1].append(checkxc)
        bcchecklist[len(bcchecklist) - 1].append(checkyc)


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

    # check if coords inside boundary or outside boundary
    windowptlist = chooseinoutcoord(xmin,xmax,ymin,ymax,xycoordlist,bcchecklist,biopsycoordinatelist)

    return windowptlist


# get biopsy coordinates
biopsycoordinatefile = GBMslidingWindowBoxMappingCoordinate.getCoordinatefiles(mapDir, coorDir)


def genTextures():

    GLCMAngleList = ['Avg']
    featureTitle = ['Image Contrast', 'Image Filename','X', 'Y', 'Boundary (1) or not (inside: 0), (outside:2)', 'Biopsy(1) or not (0)']

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
    featureTitle = featureTitle + MeanStdfeaturelist

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

            if slicenum not in biopsycoordinatefile[newpatientname]:
                continue
            else:
                biopsycoordinatelist = biopsycoordinatefile[newpatientname][slicenum]

            T1windowptlist = ParseXMLDrawROI(T1xmlfilepath,biopsycoordinatelist)
            T2windowptlist = ParseXMLDrawROI(T2xmlfilepath,biopsycoordinatelist)

            # start to do T1
            featuresOutFn = 'ROI_Texture_Map.csv'

            T1featuresOutFn = newpatientname + '_' + slicefile + '_' + 'T1' + '_' + featuresOutFn
            featuresCSVFn = os.path.join(outputDir, T1featuresOutFn)

            with open(featuresCSVFn, 'wb') as featureCSVFile:
                featureWriter = csv.writer(featureCSVFile, dialect='excel')
                featureWriter.writerow(featureTitle)

                for eachdcm in dicomnames:
                    dicomfile = dcmfiledict[eachdcm]

                    dicomfilepath = os.path.join(dcmxmlfilepath, dicomfile)

                    dicomImage = Read2DImage(dicomfilepath)

                    for eachpt in T1windowptlist:

                        meanstd = list()
                        GLCM = list()
                        LBP = list()
                        Gabor = list()

                        xcoord = int(eachpt[0])
                        ycoord = int(eachpt[1])
                        boundaryornot = int(eachpt[2])
                        biopsyornot = int(eachpt[3])

                        aFeature = [eachdcm, dicomfile, xcoord,ycoord, boundaryornot,biopsyornot]

                        subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

                        subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

                        # GLCM
                        glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

                        for GLCMAngle in GLCMAngleList:
                            for featureName in haralick_labels[:-1]:
                                GLCM.append(glcmFeatures[GLCMAngle][featureName])

                        # raw mean and std of subimage
                        Raw_mean = numpy.mean(subImage)
                        Raw_std = numpy.std(subImage)

                        meanstd.append(Raw_mean)
                        meanstd.append(Raw_std)

                        # LBP subimage
                        subImageLBP = dicomImage[ycoord - 4 - LBPRadius:ycoord + 4 + LBPRadius,
                                      xcoord - 4 - LBPRadius: xcoord + 4 + LBPRadius]

                        extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImage.max(), subImage.min())

                        # need to use extended ROI
                        LBPs = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius,
                                                                     LBPMethod)
                        for lbp in LBPs:
                            LBP.append(lbp)

                        # Gabor, width = 8
                        # use extended ROI
                        GaborFeatures = ExtendGaborFeatures.calcFeatures(dicomImage, xcoord - 4, ycoord - 4, 8, 8,
                                                                         Gaborkernel_bank, subImage.max(),
                                                                         subImage.min())

                        for gaborfeature in GaborFeatures:
                            for eachg in gaborfeature:
                                Gabor.append(eachg)

                        aFeature = aFeature + GLCM + LBP + Gabor + meanstd
                        featureWriter.writerow(aFeature)

            # start to do T2
            T2featuresOutFn = newpatientname + '_' + slicefile + '_' + 'T2' + '_' + featuresOutFn
            featuresCSVFn = os.path.join(outputDir, T2featuresOutFn)

            with open(featuresCSVFn, 'wb') as featureCSVFile:
                featureWriter = csv.writer(featureCSVFile, dialect='excel')
                featureWriter.writerow(featureTitle)

                for eachdcm in dicomnames:
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

                        aFeature = [eachdcm, dicomfile, xcoord, ycoord, boundaryornot, biopsyornot]

                        subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

                        subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())

                        # GLCM
                        glcmFeatures = GLCMFeatures.calcFeatures(subImageGLCM)

                        for GLCMAngle in GLCMAngleList:
                            for featureName in haralick_labels[:-1]:
                                GLCM.append(glcmFeatures[GLCMAngle][featureName])

                        # raw mean and std of subimage
                        Raw_mean = numpy.mean(subImage)
                        Raw_std = numpy.std(subImage)

                        meanstd.append(Raw_mean)
                        meanstd.append(Raw_std)

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
