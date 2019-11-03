# Plot CEDM 51 LE images with ROI

import cv2
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import csv
import os
import fnmatch
import numpy
import math
import SimpleITK
#import dicom
#import pylab

rootDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected'

Outputimage = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/51ImagesCheck/'
#xmlDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/BA-RCC.xml'

#txtDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/Pt1 - LE - CC_coor.txt'

#dcmDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/Pt1 - LE - CC.dcm'

#CSVDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/BA-RCC_image_largest_rec.csv'

# draw contour rectangle plots
def drawplot(contourx1,contourx2,contoury1,contoury2,color,lw):
    plt.plot([contourx1, contourx1], [contoury1, contoury2], color,linewidth =lw)
    plt.plot([contourx1, contourx2], [contoury1, contoury1], color,linewidth =lw)
    plt.plot([contourx1, contourx2], [contoury2, contoury2], color,linewidth =lw)
    plt.plot([contourx2, contourx2], [contoury1, contoury2], color,linewidth =lw)


def drawbox(xcoord,ycoord,width,height,color,w):
    localx1 = xcoord
    localx2 = xcoord + width
    localy1 = ycoord
    localy2 = ycoord + height
    drawplot(localx1, localx2, localy1, localy2, color,w)

def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


def ParseXMLDrawROI(rootDir):

    tree = ET.parse(rootDir)
    root = tree.getroot()

    childnum = 0
    xcoordlist = list()
    ycoordlist = list()

    for child in root.iter('string'):
        if not fnmatch.fnmatch(child.text,'*{*}*'):
            continue
        childnum+=1

        xcoords = str(child.text).split(',')[0]
        ycoords = str(child.text).split(',')[1]

        xc = float(xcoords.split('{')[1])
        yc = float(ycoords.split('}')[0].replace(' ',''))

        xcoordlist.append(xc)
        ycoordlist.append(yc)


    xcoordlist.append(xcoordlist[0])
    ycoordlist.append(ycoordlist[0])

    plt.plot(xcoordlist,ycoordlist,'g',linewidth = 2)


def ParseCsvDrawROI(rootDir):

    with open(rootDir, 'r') as roiFile:
        roiList = csv.DictReader(roiFile, dialect='excel')
        for aROI in roiList:
            xcoord = int(aROI['X'])
            ycoord = int(aROI['Y'])
            width = int(aROI['W'])
            height = int(aROI['H'])

            drawbox(xcoord,ycoord,width,height,'m',2)

def genLargeBoxImage(rootDir):

    for twofolder in os.listdir(rootDir):
        if twofolder.startswith('.'):
            continue
        if twofolder.startswith('..'):
            continue
        if fnmatch.fnmatch(twofolder, '*Icon*'):
            continue

        print twofolder
        rootDir2 = os.path.join(rootDir, twofolder)

        for casefile in os.listdir(rootDir2):
            if casefile.startswith('.'):
                continue
            if casefile.startswith('..'):
                continue
            if fnmatch.fnmatch(casefile, '*Icon*'):
                continue

            print casefile

            roiDicomfile = dict()
            roixmlfile = dict()
            roiCSVfile = dict()


            lesionpath = os.path.join(rootDir2, casefile)

            for lesionfile in os.listdir(lesionpath):
                if lesionfile.startswith('.'):
                    continue
                if lesionfile.startswith('..'):
                    continue
                if fnmatch.fnmatch(lesionfile, '*Icon*'):
                    continue
                if fnmatch.fnmatch(lesionfile, '*texture*'):
                    continue

                if fnmatch.fnmatch(lesionfile, '*LE*CC*dcm'):
                    roiDicomfile['LE-CC'] = lesionfile

                if fnmatch.fnmatch(lesionfile, '*LE*MLO*dcm'):
                    roiDicomfile['LE-MLO'] = lesionfile

                if fnmatch.fnmatch(lesionfile, '*CC*xml'):
                    if casefile != 'Pt24':
                        roixmlfile['LE-CC'] = lesionfile

                if fnmatch.fnmatch(lesionfile, '*MLO*xml'):
                    if casefile != 'Pt24' or 'Pt45':
                        roixmlfile['LE-MLO'] = lesionfile

                if fnmatch.fnmatch(lesionfile,'*CC*largest*csv'):
                    if casefile != 'Pt24':
                        roiCSVfile['LE-CC'] = lesionfile

                if fnmatch.fnmatch(lesionfile,'*MLO*largest*csv'):
                    if casefile != 'Pt24' or 'Pt45':
                        roiCSVfile['LE-MLO'] = lesionfile

            if casefile == 'Pt24':
                roixmlfile['LE-CC'] = 'LA-LCC1.xml'
                roixmlfile['LE-MLO'] = 'LA-LMLO1.xml'
                roiCSVfile['LE-CC'] = 'LA-LCC1_image_largest_rec.csv'
                roiCSVfile['LE-MLO'] = 'LA-LMLO1_image_largest_rec.csv'

            if casefile == 'Pt45':
                roixmlfile['LE-MLO'] = 'DDL_LMLO2.xml'
                roiCSVfile['LE-MLO'] = 'DDL_LMLO2_image_largest_rec.csv'

            phasenames = ['LE-CC','LE-MLO']

            for phase in phasenames:
                dcmfile = roiDicomfile[phase]
                dcmDir = os.path.join(lesionpath,dcmfile)

                xmlfile = roixmlfile[phase]
                xmlDir = os.path.join(lesionpath,xmlfile)

                dicomImage = Read2DImage(dcmDir)


                plt.figure(figsize=(20,15))
                plt.imshow(dicomImage, cmap='gray')

                outputDir = Outputimage + casefile + ' ' + phase + '.png'
                plt.title(casefile + ' ' + phase)
                plt.savefig(outputDir,bbox_inches='tight')
                plt.cla()
                plt.close()


                plt.figure(figsize=(20,15))
                plt.imshow(dicomImage, cmap='gray')

                ParseXMLDrawROI(xmlDir)

                imagefile = ' ROI.png'
                boxoutputDir = Outputimage + casefile + ' '+phase + imagefile
                plt.title(casefile + ' '+ phase + ' ROI')
                plt.savefig(boxoutputDir,bbox_inches='tight')
                plt.cla()
                plt.close()



genLargeBoxImage(rootDir)


