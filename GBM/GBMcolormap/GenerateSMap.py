# for JTy slice 15 maps, biopsy coord: (X,Y) = (93,109), trueY: 0.85

import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET
import re

predfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/JTy15_0410/JTy slice 15 predictions.csv'

outputMapDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/JTy15_0410/'

T2dcmfile = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/JTyFSL_slices_only/slice15/Ax_T2_FSE_IM-0001-0015.dcm'

T2xmlfile = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/JTyFSL_slices_only/slice15/ROI for Ax_T2_FSE_IM-0001-0015.xml'


# draw rectangle plot (whole rectangle and each ROI box)
def drawplot(contourx1,contourx2,contoury1,contoury2,color,width):
    plt.plot([contourx1, contourx1], [contoury1, contoury2], color,width)
    plt.plot([contourx1, contourx2], [contoury1, contoury1], color,width)
    plt.plot([contourx1, contourx2], [contoury2, contoury2], color,width)
    plt.plot([contourx2, contourx2], [contoury1, contoury2], color,width)

# draw each ROI box
def drawbox(xcoord,ycoord,color,width):
    localx1 = xcoord - 4
    localx2 = xcoord + 4
    localy1 = ycoord - 4
    localy2 = ycoord + 4
    drawplot(localx1, localx2, localy1, localy2, color,width)

# read 2D dicom image
def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray

# get predict value from prediction file
def generatexyp(predictionfile):
    predfile = predictionfile

    i = 0
    with open(predfile, 'r') as predictFile:
        predictFile.readline()
        predictFile.readline()
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')


        xlist = list()
        ylist = list()
        plist = list()
        # biopsylist = list()
        for row in rowFile:
            i+=1
            xlist.append(int(row[0]))
            ylist.append(int(row[1]))
            # biopsylist.append(int(row[3])) # for only biopsy: 0, for other: read
            # plist.append(float(row[8])) # # for only biopsy: 0, for other: read

            # if int(row[0]) == 93 and int(row[1]) == 109:
            #     print '1'
            #     plist.append(float(0.85))
            # else:
            plist.append(float(0))
    print i
    return xlist,ylist,plist

# plot xml boundary plot of dicom image
def ParseXMLDrawROI(rootDir,color,width):
    tree = ET.parse(rootDir)
    root = tree.getroot()

    xcoordlist = list()
    ycoordlist = list()

    for child in root.iter('string'):
        if not fnmatch.fnmatch(child.text,'*{*}*'):
            continue

        xcoords = str(child.text).split(',')[0]
        ycoords = str(child.text).split(',')[1]

        xc = float(xcoords.split('{')[1])
        yc = float(ycoords.split('}')[0].replace(' ',''))

        xcoordlist.append(xc)
        ycoordlist.append(yc)

    xcoordlist.append(xcoordlist[0])
    ycoordlist.append(ycoordlist[0])

    plt.plot(xcoordlist,ycoordlist,color,linewidth = width)


xlist, ylist, plist = generatexyp(predfile)

dicomImage = Read2DImage(T2dcmfile)

plt.figure(figsize=(18, 13))

cm = plt.cm.get_cmap('jet')
plt.scatter(xlist, ylist, c=plist, vmin=0, vmax=1, cmap=cm)

# change here
# biopsyY = 0.16
# biopsyY = 0.5206
# biopsyY = 0.999583493
biopsyY = 0.85
biopsyY = int(biopsyY * 100)

biox1 = 93
bioy1 = 109

# biox2 = 89
# bioy2 = 102

drawbox(biox1, bioy1, 'm.-', 3)
plt.plot(biox1, bioy1, 'm+')
plt.text(200, 45 + 10, str(biopsyY) + '%', fontsize=25, color='magenta')
plt.annotate('', xy=(biox1, bioy1), xytext=(200, 45 + 10),
             arrowprops=dict(facecolor='magenta', width=2, shrink=0.04))

# drawbox(biox2, bioy2, 'm.-', 3)
# plt.plot(biox2, bioy2, 'm+')
# plt.text(200, 45 + 10*2, str(biopsyY) + '%', fontsize=25, color='magenta')
# plt.annotate('', xy=(biox2, bioy2), xytext=(200, 45 + 10*2),
#              arrowprops=dict(facecolor='magenta', width=2, shrink=0.04))
#

ParseXMLDrawROI(T2xmlfile,'b',0.5)

plt.colorbar()
plt.imshow(dicomImage, cmap='gray')

#plt.title('JTy slice 15 PI', fontsize=30)
# plt.title('JTy slice 15: ML gA = 0.08',fontsize =30)
# plt.title('JTy slice 15: ML-PI gA = 0.001, gl=0.01, alpha = 20',fontsize =30)
plt.title('JTy slice 15: Biopsies',fontsize =30)


# to do: change image name by column name
# plt.savefig(outputMapDir + 'JTy slice 15 PI' + '.png')
# plt.savefig(outputMapDir + 'JTy slice 15 ML' + '.png')
# plt.savefig(outputMapDir + 'JTy slice 15 ML-PI' + '.png')
plt.savefig(outputMapDir + 'JTy slice 15 Biopsy' + '.png')
plt.cla()
plt.close()


