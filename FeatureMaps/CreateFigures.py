import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET

dcmfile = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM-51/malignant/Pt50/Pt50 - LE - CC.dcm'

xmlfile = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM-51/malignant/Pt50/VES_LCC.xml'

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

    return xcoordlist,ycoordlist
    # plt.plot(xcoordlist,ycoordlist,color,linewidth = width)


# read 2D dicom image
def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


def GrayScaleNormalization(imgArray, imgMax,imgMin):

    # try:
    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    # transfer to closest int
    imgArray = np.rint(imgArray).astype(np.int16)

    # except ValueError:
    #     pass
    return imgArray




dicomImage = Read2DImage(dcmfile)


# plt.figure(figsize= (18,13))
plt.figure(figsize=(20,15))

xcoordlist, ycoordlist = ParseXMLDrawROI(xmlfile,'r',2)

plt.imshow(dicomImage,cmap='gray')
# xcoord = 141
# ycoord = 2332
# width = 180
# height = 161

#

xlarge = max(xcoordlist)
xsmall = min(xcoordlist)
ylarge = max(ycoordlist)
ysmall = min(ycoordlist)

width = xlarge - xsmall
height = ylarge - ysmall

drawbox(xsmall,ysmall,width,height,'r',2)

# plt.show()
imgpath = '/Users/yanzhexu/Desktop/Research/featureMap/Pt50Figures/'
title = 'Pt50 LE CC ROI Box'
plt.title(title)
plt.savefig(imgpath + title + '.png',bbox_inches='tight')
plt.cla()
plt.close()


# plt.scatter(xlist, ylist, c=featurelist, alpha=0.5, cmap='gray')
# # plt.imshow(np.transpose(z),alpha= 1,cmap= 'gray') # change interpolation: "bilinear"
# # plt.colorbar()
# # plt.imshow(ImageArray,alpha=0.6,cmap='gray')
#
# plt.imshow(ImageArray,alpha = 1, cmap='gray')
# #

# title = 'Pt1 LE CC'
# plt.savefig(imgpath + title + '.png')
# plt.cla()
# plt.close()

# fig, (ax0, ax1) = plt.subplots(ncols=2,
#                                figsize=(12, 4),
#                                sharex=True,
#                                sharey=True,
#                                subplot_kw={"adjustable": "box-forced"})
# En = entropy(subImage, disk(5))
#
# print En
#
#
# plt.imshow(En, cmap='gray')
# # plt.set_title("Entropy")
# # ax1.axis("off")

# plt.title('')
# plt.tight_layout()
#






