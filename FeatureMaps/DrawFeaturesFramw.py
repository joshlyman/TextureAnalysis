# Experiment: test if xml file and txt file are same for CEDM sliding window test

import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import csv
import os
import fnmatch
import numpy
import math
import SimpleITK

xmlDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM-51/benign/Pt1/BA-RCC.xml'

#txtDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/Pt1 - LE - CC_coor.txt'

dcmDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM-51/benign/Pt1/Pt1 - LE - CC.dcm'

CSVDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM-51/benign/Pt1/BA-RCC_image_largest_rec.csv'

outDir = '/Users/yanzhexu/Desktop/Research/featureMap/'

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

    plt.plot(xcoordlist,ycoordlist,'g',linewidth = 0.5)


def ParseCsvDrawROI(rootDir):

    with open(rootDir, 'r') as roiFile:
        roiList = csv.DictReader(roiFile, dialect='excel')
        for aROI in roiList:
            xcoord = int(aROI['X'])
            ycoord = int(aROI['Y'])
            width = int(aROI['W'])
            height = int(aROI['H'])

            xcoord = 2300
            ycoord = 1700
            width = 200
            height = 400

            print 'X:', xcoord
            print 'Y:', ycoord
            print 'W:', width
            print 'H:', height

            # xcoord = 1620
            # width = 66
            #width = 150
            # height = 335
            # height = 284
            # xcoord = 570
            # height = 108
            # ycoord = 1552
            # height = 59
            # width = 80
            # width = 54
            # xcoord = 418
            # width = 305
            # ycoord = 1496
            # height = 94

            drawbox(xcoord,ycoord,width,height,'r',0.5)



# plt.figure()
dicomImage = Read2DImage(dcmDir)
plt.imshow(dicomImage,cmap='gray')
ParseXMLDrawROI(xmlDir)
ParseCsvDrawROI(CSVDir)
plt.show()

Ptcase ='Pt1 LE CC'
png = '.png'
saveDir = outDir + Ptcase + png
title = Ptcase

plt.title(title)
# plt.savefig(saveDir,bbox_inches='tight')
plt.cla()
plt.close()


