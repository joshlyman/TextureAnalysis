# for JTy slice 15 maps, biopsy coord: (X,Y) = (93,109), trueY: 0.85

import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET
from scipy.interpolate import interp2d
import re

predfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/CE22_0413/NewPDGFRA2.csv' #NewEGFR2

outputMapDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/CE22_0413/'

T2dcmfile = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22/Ax_T2_FSE_IM-0001-0022.dcm'

T2xmlfile = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22/ROI for Ax_T2_FSE_IM-0001-0022.xml'


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

# get predict value from prediction file
def generatexyp(predictionfile):
    predfile = predictionfile

    i = 0
    with open(predfile, 'r') as predictFile:
        # predictFile.readline()
        # predictFile.readline()
        # predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')


        xlist = list()
        ylist = list()
        plist = list()
        # biopsylist = list()
        for row in rowFile:
            i+=1
            xlist.append(int(row[0]))
            ylist.append(int(row[1]))
            plist.append(float(row[2]))
            # biopsylist.append(int(row[3])) # for only biopsy: 0, for other: read
            # plist.append(float(row[8])) # # for only biopsy: 0, for other: read

            # if int(row[0]) == 93 and int(row[1]) == 109:
            #     print '1'
            #     plist.append(float(0.85))
            # else:
            # plist.append(float(0))
    print i
    return xlist,ylist,plist

# plot xml boundary plot of dicom image
def ParseXMLDrawROI(rootDir,color,width):
    tree = ET.parse(rootDir)
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

    xcoordlist.append(xcoordlist[0])
    ycoordlist.append(ycoordlist[0])

    plt.plot(xcoordlist,ycoordlist,color,linewidth = width)

    return xycoordlist

xlist, ylist, plist = generatexyp(predfile)


dicomImage = Read2DImage(T2dcmfile)

plt.figure(figsize=(18, 13))

# X,Y = np.meshgrid(xlist,ylist)


# cm = plt.cm.get_cmap('jet')
# plt.scatter(xlist, ylist, c=plist, vmin=0, vmax=1, cmap=cm,interpolation = 'bilinear')


# data = np.random.random((30,30))
# X = np.arange(0, 30, 1)
# Y = np.arange(0, 30, 1)



xycoord = ParseXMLDrawROI(T2xmlfile,'b',0.5)




# xm, ym = np.mgrid[0:256:1, 0:256:1]
z = np.zeros((256,256))

for i in range(len(xlist)):
    xc = xlist[i]
    yc = ylist[i]

    pc = plist[i]


    inorout = point_inside_polygon(xc,yc,xycoord)

    # if inside plot, set it to p value, if not, set it 0
    if inorout == True:
        z[xc][yc] = pc
    else:
        z[xc][yc] = 0


cm = plt.cm.get_cmap('jet')
# plt.imshow(z,vmin = 0,vmax = 1, cmap = cm, interpolation="nearest")

# plt.pcolormesh(xm, ym, z,alpha=0.2, cmap=cm,shading='gouraud')
plt.imshow(np.transpose(z),alpha = 1,vmin=0, vmax=1, cmap=cm,interpolation='bicubic') # change interpolation: "bilinear"
plt.colorbar()
plt.imshow(dicomImage, alpha=0.5,cmap='gray')
# plt.pcolor(xm,ym, z,alpha = 0.5,vmin=0, vmax=1, cmap=cm,edgecolors="none")




# change here
# biopsyY = 0.16
# biopsyY = 0.5206
# biopsyY = 0.999583493
# biopsyY = 0.85
# biopsyY = int(biopsyY * 100)
#
# biox1 = 93
# bioy1 = 109
#
# # biox2 = 89
# # bioy2 = 102
#
# drawbox(biox1, bioy1, 'm.-', 3)
# plt.plot(biox1, bioy1, 'm+')
# plt.text(200, 45 + 10, str(biopsyY) + '%', fontsize=25, color='magenta')
# plt.annotate('', xy=(biox1, bioy1), xytext=(200, 45 + 10),
#              arrowprops=dict(facecolor='magenta', width=2, shrink=0.04))

# drawbox(biox2, bioy2, 'm.-', 3)
# plt.plot(biox2, bioy2, 'm+')
# plt.text(200, 45 + 10*2, str(biopsyY) + '%', fontsize=25, color='magenta')
# plt.annotate('', xy=(biox2, bioy2), xytext=(200, 45 + 10*2),
#              arrowprops=dict(facecolor='magenta', width=2, shrink=0.04))
#

# ParseXMLDrawROI(T2xmlfile,'b',0.5)
#
# plt.colorbar()
# plt.imshow(dicomImage, cmap='gray')

#plt.title('JTy slice 15 PI', fontsize=30)
# plt.title('JTy slice 15: ML gA = 0.08',fontsize =30)
# plt.title('JTy slice 15: ML-PI gA = 0.001, gl=0.01, alpha = 20',fontsize =30)
plt.title('CE slice 22 PDGFRA Alpha 45000',fontsize =30)


# to do: change image name by column name
# plt.savefig(outputMapDir + 'JTy slice 15 PI' + '.png')
# plt.savefig(outputMapDir + 'JTy slice 15 ML' + '.png')
# plt.savefig(outputMapDir + 'JTy slice 15 ML-PI' + '.png')
plt.savefig(outputMapDir + 'CE slice 22 PDGFRA Alpha45000' + '.png')
plt.cla()
plt.close()


