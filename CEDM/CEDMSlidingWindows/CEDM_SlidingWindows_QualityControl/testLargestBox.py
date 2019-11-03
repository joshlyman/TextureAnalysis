# Plot CEDM images with ROI and updated largest box after correcting the box size to avoid noise
#


import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import csv
import os
import fnmatch
import numpy
import math
import SimpleITK

xmlDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/Marley Grant Data_0410/Marley Grant Data/B14 - B14/Standard 2D Contrast/B14_CC.xml'

#txtDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/Pt1 - LE - CC_coor.txt'

dcmDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/Marley Grant Data_0410/Marley Grant Data/B14 - B14/Standard 2D Contrast/L CC LE - 71100000/IM-0001-0056-0001.dcm'

CSVDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/Marley Grant Data_0410/Marley Grant Data/B14 - B14/Standard 2D Contrast/L CC LE - 71100000/B14_CC_image_largest_rec.csv'

outDir = '/Users/yanzhexu/Desktop/Research/CEDM_ROI_QualityControl/CEDM_Update/Updatedcheck/'

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

            # ycoord = 2122
            # height = 88
            # xcoord = 2653
            # width = 149

            # ycoord = 1446
            # height = 113

            # ycoord = 1894
            # height = 87

            # xcoord = 2256
            # width = 287

            # height = 20

            # height = 40


            drawbox(xcoord,ycoord,width,height,'r',0.5)



# plt.figure()
dicomImage = Read2DImage(dcmDir)
plt.imshow(dicomImage,cmap='gray')
ParseXMLDrawROI(xmlDir)
ParseCsvDrawROI(CSVDir)
# plt.show()

Ptcase = 'B14 CC Updated LargestBox'
png = '.png'
saveDir = outDir + Ptcase + png
title = Ptcase


plt.title(title)
plt.savefig(saveDir,bbox_inches='tight')
plt.cla()
plt.close()








