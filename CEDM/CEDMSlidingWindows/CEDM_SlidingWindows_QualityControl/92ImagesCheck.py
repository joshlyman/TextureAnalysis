# Plot CEDM 92 LE images with ROI

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

rootDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/Marley Grant Data'

Outputimage = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/92ImagesCheck/'
#xmlDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/BA-RCC.xml'

#txtDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/Pt1 - LE - CC_coor.txt'

#dcmDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/Pt1 - LE - CC.dcm'

#CSVDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/BA-RCC_image_largest_rec.csv'

# draw contour rectangle plots
def drawplot(contourx1,contourx2,contoury1,contoury2,color,lw):
    plt.plot([contourx1, contourx1], [contoury1, contoury2], color,linewidth =lw )
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

        print casefile

        casename = casefile.split('-')[0]

        lesionpath = os.path.join(rootDir, casefile)

        for folder2 in os.listdir(lesionpath):
            if folder2.startswith('.'):
                continue
            if folder2.startswith('..'):
                continue
            if fnmatch.fnmatch(folder2, '*Icon*'):
                continue
            if fnmatch.fnmatch(folder2,'*roi*'):
                continue

            lesionpath2 = os.path.join(lesionpath,folder2)
            print lesionpath2

            phasefile = dict()
            phasenames = ['LE-CC', 'LE-MLO']
            roiDicomfile = dict()
            roixmlfile = dict()
            roiCSVfile = dict()

            for lesionfile in os.listdir(lesionpath2):

                if lesionfile.startswith('.'):
                    continue
                if lesionfile.startswith('..'):
                    continue
                if fnmatch.fnmatch(lesionfile, '*Icon*'):
                    continue
                if fnmatch.fnmatch(lesionfile, '*texture*'):
                    continue

                if fnmatch.fnmatch(lesionfile,'*CC*LE*'):
                    phasefile['LE-CC'] = lesionfile

                if fnmatch.fnmatch(lesionfile,'*MLO*LE*'):
                    phasefile['LE-MLO'] = lesionfile

                if fnmatch.fnmatch(lesionfile, '*CC*xml'):
                    roixmlfile['LE-CC'] = lesionfile

                if fnmatch.fnmatch(lesionfile, '*MLO*xml'):
                    roixmlfile['LE-MLO'] = lesionfile

            for phase in phasenames:
                print phase
                lesionfolder = phasefile[phase]
                print lesionfolder

                lesionpath3 = os.path.join(lesionpath2,lesionfolder)

                for file in os.listdir(lesionpath3):
                    if file.startswith('.'):
                        continue
                    if file.startswith('..'):
                        continue
                    if fnmatch.fnmatch(file, '*Icon*'):
                        continue

                    if fnmatch.fnmatch(file,'*texture*largest*csv'):
                        continue

                    if fnmatch.fnmatch(file,'*largest*csv'):
                        roiCSVfile[phase] = file
                    if fnmatch.fnmatch(file,'*dcm'):
                        roiDicomfile[phase] = file


            for phase in phasenames:
                lesionfolder = phasefile[phase]

                lesionpath3 = os.path.join(lesionpath2, lesionfolder)

                dcmfile = roiDicomfile[phase]
                dcmDir = os.path.join(lesionpath3,dcmfile)

                largeboxfile = roiCSVfile[phase]
                CSVDir = os.path.join(lesionpath3,largeboxfile)

                xmlfile = roixmlfile[phase]
                xmlDir = os.path.join(lesionpath2, xmlfile)

                dicomImage = Read2DImage(dcmDir)

                #pylab.show()

                plt.figure(figsize=(20,15))
                plt.imshow(dicomImage, cmap='gray')
                #dicomImage = dicom.read_file(dcmDir)
                #pylab.imshow(dicomImage, cmap='gray')
                outputDir = Outputimage + casename + ' ' + phase + '.png'
                plt.title(casename + ' ' + phase)
                plt.savefig(outputDir,bbox_inches='tight')
                plt.cla()
                plt.close()


                plt.figure(figsize=(20,15))
                plt.imshow(dicomImage, cmap='gray')

                #dicomImage = dicom.read_file(dcmDir)
                #pylab.imshow(dicomImage, cmap='gray')
                ParseXMLDrawROI(xmlDir)
                #ParseCsvDrawROI(CSVDir)

                imagefile = ' ROI.png'
                boxoutputDir = Outputimage + casename + ' '+phase + imagefile
                plt.title(casename + ' '+ phase + ' ROI')
                plt.savefig(boxoutputDir,bbox_inches='tight')
                plt.cla()
                plt.close()



genLargeBoxImage(rootDir)


