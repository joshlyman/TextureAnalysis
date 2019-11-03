import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET

import re
from skimage import data
from skimage.util import img_as_ubyte
from skimage.filters.rank import entropy
from skimage.morphology import disk

# featurefile = '/Users/yanzhexu/Desktop/Research/featureMap/Pt1_benign_ROI_Texture_Map.csv'
# featurefile = '/Users/yanzhexu/Desktop/Research/featureMap/Pt9_malignant_ROI_Texture_Map.csv'

featurefile = '/Users/yanzhexu/Desktop/Research/Sliding box CEDM/addYlabel/CEDM_TextureMap_51/Pt7_benign_ROI_Texture_Map.csv'

# featurefile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addPI/GBM_SlidingWindow_TextureMap_addPI/CE_slice22_T2_ROI_Texture_Map.csv' #NewEGFR2

dcmfile = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM-51/benign/Pt7/Pt7 - LE - CC.dcm'

xmlfile = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM-51/benign/Pt7/LL-RCC2.xml'



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

with open(featurefile,'r') as readfile:
    readfile.readline()

    rowFile = csv.reader(readfile, delimiter=',')

    xlist = list()
    ylist = list()
    featurelist = list()
    for row in rowFile:
        if row[3] == 'LE-CC':
        # if row[0] =='EPI':
            # sldx = int(row[2])
            # sldy = int(row[3])
            # entropy = float(row[15])
            sldx = int(row[4])
            sldy = int(row[5])
            entropy = float(row[31]) # 16: Difference Variance Average , 21: LBP01 31: Gabor std mean = 0.6, freq = 0.3

            xlist.append(sldx)
            ylist.append(sldy)
            featurelist.append(entropy)
        else:
            continue




dicomImage = Read2DImage(dcmfile)


print np.shape(dicomImage)
# # print dicomImage
#
#
# x1 = 1818
# width = 144
# y1 = 2435
# height = 144
#
# subImage = dicomImage[y1:(y1 + height), x1:(x1 + width)]

ImageArray = GrayScaleNormalization(dicomImage,dicomImage.max(),dicomImage.min())


# print ImageArray
# print ImageArray.shape


plt.figure(figsize= (18,13))
# plt.figure()
# plt.figure(figsize=(20,15))
# xm, ym = np.mgrid[0:2600:1, 0:2600:1]
z = np.zeros((2560,3328))

for i in range(len(xlist)):
    xc = xlist[i]
    yc = ylist[i]

    pc = featurelist[i]

    z[xc][yc] = pc

print np.std(z)

print np.shape(z)

# z = GrayScaleNormalization(z,z.max(),z.min())
# cm = plt.cm.get_cmap('jet')
#



# ParseXMLDrawROI(xmlfile,'r',0.5)

plt.scatter(xlist, ylist, c=featurelist, alpha=0.5, cmap='hot')
# plt.imshow(np.transpose(z),alpha= 1,cmap= 'gray') # change interpolation: "bilinear"
# plt.colorbar()
# plt.imshow(ImageArray,alpha=0.6,cmap='gray')

plt.imshow(ImageArray,alpha = 1, cmap='gray')
#

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
# plt.show()
imgpath = '/Users/yanzhexu/Desktop/Research/featureMap/FeatureMaps0501/'
title = 'Pt7 Benign LE CC Gabor Feature Map'
plt.title(title)
plt.savefig(imgpath + title + '.png',bbox_inches='tight')
plt.cla()
plt.close()






