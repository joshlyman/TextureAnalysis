# update Raw features: add Patient by patient T2 based normalization raw features inside.

# Patient by patient T2 based normalization: for each patient and each contrast, get all slices together and
# find all T2 box area's box and get range from it.

import os
import csv
import fnmatch
import SimpleITK
import numpy
import xml.etree.ElementTree as ET
import math


rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'

texturesPath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addYlabel/GBM_SlidingWindow_TextureMap'

outputpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/AddPtbyPtT2NormedRawMeaninside/'


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

    return xmin, xmax, ymin, ymax, xycoordlist


def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


def Norm_Mean_Std_LargestBox(imgArray,imgMax,imgMin):

    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    meang = numpy.mean(imgArray)
    stdg = numpy.std(imgArray)

    return meang,stdg


contrastslist = ['EPI','SPGRC','T2','P','Q','RCBV']

def getpatientslicedict(texturesPath):
    patientslicedict = dict()

    for texturesfile in os.listdir(texturesPath):
        if texturesfile.startswith('.'):
            continue
        if texturesfile.startswith('..'):
            continue

        print texturesfile

        patient = texturesfile.split('_')[0]
        slicenum = texturesfile.split('_')[1].split('slice')[1]

        if patient not in patientslicedict:
            patientslicedict[patient] = list()
        patientslicedict[patient].append(slicenum)

    return patientslicedict


# get patient contrast range dict
def getPtsContrastRange(texturesPath,rootDir):

    patientslicedict = getpatientslicedict(texturesPath)

    # patient - contrast - min/max
    PtsContrastMin = dict()
    PtsContrastMax = dict()

    for patient in patientslicedict:

        slicenumlist = patientslicedict[patient]

        print 'patient:',patient
        print 'slices:',slicenumlist

        # for each patient, find corresponding casefolder
        for casefolder in os.listdir(rootDir):
            if casefolder.startswith('.'):
                continue
            if casefolder.startswith('..'):
                continue

            if fnmatch.fnmatch(casefolder,'*'+str(patient)+'*'):
                print casefolder

                casefolderpath = os.path.join(rootDir, casefolder)

                PtsContrastMin[casefolder] = dict()
                PtsContrastMax[casefolder] = dict()

                slicesContrastdcmdict = dict()

                # for each slice, get 6 contrasts' dcm files
                for slicenum in slicenumlist:
                    slicefolder = 'slice' + str(slicenum)
                    slicefolderpath = os.path.join(casefolderpath,slicefolder)

                    # slicenum - contrast - dcm file name
                    slicesContrastdcmdict[slicenum] = dict()

                    for dcmfile in os.listdir(slicefolderpath):

                        if dcmfile.startswith('.'):
                            continue
                        if fnmatch.fnmatch(dcmfile, '*dcm*') is False:
                            continue
                        if fnmatch.fnmatch(dcmfile, '*precontrast*'):
                            continue

                        if fnmatch.fnmatch(dcmfile, '*C*SPGR*') or fnmatch.fnmatch(dcmfile, '*+C*T1*') or fnmatch.fnmatch(
                                dcmfile, '*T1*+C*'):
                            SPGRCfile = dcmfile
                            slicesContrastdcmdict[slicenum]['SPGRC'] = SPGRCfile

                        if fnmatch.fnmatch(dcmfile, '*T2*'):
                            T2file = dcmfile
                            slicesContrastdcmdict[slicenum]['T2'] = T2file

                        if fnmatch.fnmatch(dcmfile, '*q*'):
                            Qfile = dcmfile
                            slicesContrastdcmdict[slicenum]['Q'] = Qfile

                        if fnmatch.fnmatch(dcmfile, '*p*'):
                            Pfile = dcmfile
                            slicesContrastdcmdict[slicenum]['P'] = Pfile

                        if fnmatch.fnmatch(dcmfile, '*rCBV*'):
                            RCBVfile = dcmfile
                            slicesContrastdcmdict[slicenum]['RCBV'] = RCBVfile

                        if fnmatch.fnmatch(dcmfile, '*EPI*+C*') or fnmatch.fnmatch(dcmfile, '*+C*EPI*'):
                            EPIfile = dcmfile
                            slicesContrastdcmdict[slicenum]['EPI'] = EPIfile


                    for xmlfile in os.listdir(slicefolderpath):
                        if not fnmatch.fnmatch(xmlfile, '*.xml'):
                            continue
                        if fnmatch.fnmatch(xmlfile, '*T2*'):
                            T2xmlfile = xmlfile


                    print '\n'

                    T2xmlfilepath = os.path.join(slicefolderpath, T2xmlfile)

                    T2xmin, T2xmax, T2ymin, T2ymax, T2xycoord = ParseXMLDrawROI(T2xmlfilepath)

                    slicesContrastdcmdict[slicenum]['T2xmin'] = T2xmin
                    slicesContrastdcmdict[slicenum]['T2xmax'] = T2xmax
                    slicesContrastdcmdict[slicenum]['T2ymin'] = T2ymin
                    slicesContrastdcmdict[slicenum]['T2ymax'] = T2ymax

                    print slicesContrastdcmdict[slicenum]

                # for each contrast, combine each slice's dcm file
                for contrast in contrastslist:
                    PtsContrastMin[casefolder][contrast] = list()
                    PtsContrastMax[casefolder][contrast] = list()

                    for slicenum2 in slicesContrastdcmdict:
                        contrastDicom = slicesContrastdcmdict[slicenum2][contrast]

                        xmin = slicesContrastdcmdict[slicenum2]['T2xmin']
                        xmax = slicesContrastdcmdict[slicenum2]['T2xmax']
                        ymin = slicesContrastdcmdict[slicenum2]['T2ymin']
                        ymax = slicesContrastdcmdict[slicenum2]['T2ymax']

                        slicefolder = 'slice' + str(slicenum2)

                        slicefolderpath = os.path.join(casefolderpath,slicefolder)

                        dcmfilepath = os.path.join(slicefolderpath,contrastDicom)
                        dicomImage = Read2DImage(dcmfilepath)
                        subImage = dicomImage[ymin:ymax,xmin:xmax]

                        subImageMin = numpy.min(subImage)
                        PtsContrastMin[casefolder][contrast].append(subImageMin)

                        subImageMax = numpy.max(subImage)
                        PtsContrastMax[casefolder][contrast].append(subImageMax)

    # print PtsContrastMin
    # print PtsContrastMax


    return PtsContrastMin,PtsContrastMax


# getPtsContrastRange(texturesPath,rootDir)


# Main function: update raw features
def updatePPRawMeanStd(texturesPath,rootDir):

    # get patient-contrast-Min/Max dict
    PtsContrastMin, PtsContrastMax = getPtsContrastRange(texturesPath,rootDir)

    for texturesfile in os.listdir(texturesPath):
        if texturesfile.startswith('.'):
            continue
        if texturesfile.startswith('..'):
            continue

        print texturesfile

        patient = texturesfile.split('_')[0]
        slicenum = texturesfile.split('_')[1].split('slice')[1]

        texturesfilepath = os.path.join(texturesPath, texturesfile)

        for casefolder in os.listdir(rootDir):
            if casefolder.startswith('.'):
                continue

            if casefolder.startswith('.'):
                continue

            if fnmatch.fnmatch(casefolder, '*' + str(patient) + '*'):
                print casefolder

                print '\n'

                slicefolder = 'slice' + str(slicenum)
                casefolderpath = os.path.join(rootDir, casefolder)
                slicefolderpath = os.path.join(casefolderpath, slicefolder)

                dcmfiledict = dict()
                for dcmfile in os.listdir(slicefolderpath):

                    if dcmfile.startswith('.'):
                        continue
                    if fnmatch.fnmatch(dcmfile, '*dcm*') is False:
                        continue
                    if fnmatch.fnmatch(dcmfile, '*precontrast*'):
                        continue

                    if fnmatch.fnmatch(dcmfile, '*C*SPGR*') or fnmatch.fnmatch(dcmfile, '*+C*T1*') or fnmatch.fnmatch(
                            dcmfile, '*T1*+C*'):
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

                outputfeaturefilepath = os.path.join(outputpath, texturesfile)

                with open(outputfeaturefilepath, 'wb') as writefile:
                    featureWriter = csv.writer(writefile, dialect='excel')

                    with open(texturesfilepath, 'r') as featuresfile:
                        # featuresfile.readline()
                        rowFile = csv.reader(featuresfile, delimiter=',')

                        for row in rowFile:
                            if row[0] == 'Image Contrast':
                                row.insert(42, 'Patient by Patient T2 based Normalized Raw Mean')
                                row.insert(43, 'Patient by Patient T2 based Normalized Raw Std')
                                featureWriter.writerow(row)
                            else:
                                contrast = row[0]
                                dcmfile = dcmfiledict[contrast]
                                dcmfilepath = os.path.join(slicefolderpath, dcmfile)

                                xcoord = int(row[2])
                                ycoord = int(row[3])

                                dicomImage = Read2DImage(dcmfilepath)

                                subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]

                                # get Max/Min lists of each patient's slices and get range
                                RawMax = numpy.max(PtsContrastMax[casefolder][contrast])
                                RawMin = numpy.min(PtsContrastMin[casefolder][contrast])

                                Raw_mean, Raw_std = Norm_Mean_Std_LargestBox(subImage, RawMax, RawMin)

                                row.insert(42, Raw_mean)
                                row.insert(43, Raw_std)

                                featureWriter.writerow(row)


updatePPRawMeanStd(texturesPath,rootDir)