# only process 1 patient and 1 slice

import csv
import os
import xml.etree.ElementTree as ET
import fnmatch
import numpy
import math
import SimpleITK
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
# biopsy: 3 conditions: 1. in boundary 2. off boundary but in rectangle box 3. off boundary and out of box
def T2chooseinoutcoord(contourx1,contourx2,contoury1,contoury2,T2xycoord):

    windowptlist = list()

    # for each point inside rectangle plot, check if each point inside boundary or outside boundary, inside: True, outside: False
    for testx in range(contourx1,contourx2+1):
        for testy in range(contoury1,contoury2+1):

            # check if point is inside T2 boundary or not
            T2inorout = point_inside_polygon(testx, testy, T2xycoord)

            if T2inorout == True:

                windowptlist.append(list())
                windowptlist[len(windowptlist)-1].append(testx)
                windowptlist[len(windowptlist)-1].append(testy)

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


def genTextures(rootDir,outputDir,phasename,patient,slicenum,GLCMdist,LBPrad,GLCM,LBP,GABOR,RAW):

    featureTitle = ['Phase','ROI_X','ROI_Y']

    if GLCM == True:
        GLCMAngleList = ['Avg']
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
        MeanStdLBfeaturelist = ['Raw Mean', 'Raw Std']
        featureTitle = featureTitle + MeanStdLBfeaturelist

    Ylabel = ['Ylabel']

    featureTitle = featureTitle + Ylabel


    for texturemapfile in os.listdir(rootDir):

        if texturemapfile.startswith('.'):
            continue
        if texturemapfile.startswith('..'):
            continue

        if fnmatch.fnmatch(texturemapfile,'*'+patient+'*'):

            slicepathfile = os.path.join(rootDir, texturemapfile)

            slicefile = 'slice' + slicenum

            print slicefile

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

                if fnmatch.fnmatch(xmlfile, '*T2*'):
                    T2xmlfile = xmlfile


            print '\n'

            T2xmlfilepath = os.path.join(dcmxmlfilepath, T2xmlfile)

            T2xmin, T2xmax, T2ymin, T2ymax, T2xycoord = ParseXMLDrawROI(T2xmlfilepath)

            # check if coords inside boundary or outside boundary
            T2windowptlist = T2chooseinoutcoord(T2xmin, T2xmax, T2ymin, T2ymax,T2xycoord)

            # start to do T1
            featuresOutFn = 'ROI_Texture_Map.csv'

            # start to do T2
            T2featuresOutFn = patient + '_' + slicefile + '_' + 'T2' + '_'+phasename + '_' + featuresOutFn
            featuresCSVFn = os.path.join(outputDir, T2featuresOutFn)

            with open(featuresCSVFn, 'wb') as featureCSVFile:
                featureWriter = csv.writer(featureCSVFile, dialect='excel')
                featureWriter.writerow(featureTitle)

                dicomfile = dcmfiledict[phasename]

                dicomfilepath = os.path.join(dcmxmlfilepath, dicomfile)

                dicomImage = Read2DImage(dicomfilepath)

                for eachpt in T2windowptlist:

                    xcoord = int(eachpt[0])
                    ycoord = int(eachpt[1])

                    aFeature = [phasename, xcoord, ycoord]

                    subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

                    # GLCM
                    if GLCM == True:
                        GLCMAngleList = ['Avg']
                        subImageGLCM = GrayScaleNormalization(subImage, subImage.max(), subImage.min())
                        glcmFeatures = GLCM_GUI.calcFeatures(subImageGLCM, GLCMdist)

                        for GLCMAngle in GLCMAngleList:
                            for featureName in haralick_labels[:-1]:
                                aFeature.append(glcmFeatures[GLCMAngle][featureName])

                    # LBP
                    if LBP == True:
                        LBPRadius = LBPrad
                        LBPnPoints = 8 * LBPRadius
                        LBPMethod = 'uniform'

                        subImageLBP = dicomImage[ycoord - 4 - LBPRadius:ycoord + 4 + LBPRadius,
                                  xcoord - 4 - LBPRadius: xcoord + 4 + LBPRadius]

                        # for extended LBP, we still use grayscale range of 8*8 box to normalize extended ROI 10*10 box
                        extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImage.max(), subImage.min())

                        # need to use extended ROI
                        lbpFeatures = ExtendLBP_GUI.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius,
                                                                 LBPMethod)
                        aFeature = aFeature + lbpFeatures.tolist()

                    # Gabor
                    if GABOR == True:
                        GaborFeatures = ExtendGaborFeatures_GUI.calcFeatures(dicomImage, xcoord - 4, ycoord - 4,
                                                                         8, 8,
                                                                         Gaborkernel_bank, subImage.max(),
                                                                         subImage.min())
                        for gaborfeature in GaborFeatures:
                            aFeature = aFeature + gaborfeature.tolist()


                    if RAW == True:
                        ## get mean and standard deviation of lesion ROI's gray level of lagest box directly from subImage
                        mean_LargBox = numpy.mean(subImage)
                        std_LargBox = numpy.std(subImage)
                        aFeature = aFeature + [mean_LargBox, std_LargBox]

                    featureWriter.writerow(aFeature)



rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'

outputDir = '/Users/yanzhexu/Desktop/Research/TA GUI/GBM/'


# parameter:
# 1. rootDir: input path of dataset folder
# 2. outputDir: output path to store each sliding window textures file
# 3. phasename: modality: 'EPI', 'P', 'Q', 'RCBV', 'SPGRC', 'T2'
# 4. patient: 'CG','EB','ET','SA','SF','SH','VBr','CE','JM','JTy','MW','NT','PC','RA','RGl','RGr','Rlv','RWh'
# 5. slicenum: which slice of patient to choose
# 6. GLCMdist: GLCM distance
# 7. LBPrad: LBP radius
# 8. GLCM, LBP, GABOR, RAW: add/delete 4 features: True/False


genTextures(rootDir,outputDir,phasename='P',patient='CE',slicenum ='22',GLCMdist=1,LBPrad=1,GLCM=False,LBP=True,GABOR=True,RAW=True)
