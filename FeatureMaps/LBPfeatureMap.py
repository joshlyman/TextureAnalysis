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
from skimage.feature import local_binary_pattern

dcmfile = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM-51/malignant/Pt9/Pt9 - LE - CC.dcm'
xmlfile = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM-51/malignant/Pt9/RT-LCC.xml'
featureDir = '/Users/yanzhexu/Desktop/Research/featureMap/'

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

# read 2D dicom image
def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


dicomImage = Read2DImage(dcmfile)

# contourx1 = 10
# contourx2 = 500
# contoury1 = 560
# contoury2 = 1260

contourx1 = 10
contourx2 = 2500
contoury1 = 400
contoury2 = 4000

nPoints = 8
radius = 1
method = 'uniform'

def genLBPfeatures():

    CSVFn = 'Pt9_LBPfeatures_onlycenter_s3.csv'
    featureCSVFn = featureDir + CSVFn

    featureTitle = ['X','Y','LBP pattern']

    # for each point with interval 8 inside rectangle plot, check if each point inside boundary or outside boundary, inside: True, outside: False

    with open(featureCSVFn, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')
        featureWriter.writerow(featureTitle)

        for testx in range(contourx1,contourx2+1,3):
            for testy in range(contoury1,contoury2+1,3):

                subImage = dicomImage[testy - 1:testy + 2, testx - 1:testx + 2]
                lbp = local_binary_pattern(subImage, nPoints, radius, method)


                # for jy in range(-1,1):
                #     for ix in range(-1,1):
                #         y = testy +jy
                #         x = testx +ix
                #
                #         lbpvalue = lbp[jy+1][ix+1]

                # print np.shape(lbp)
                # print lbp
                x = testx
                y = testy
                lbpvalue = lbp[2][2]
                rowlist = [str(x),str(y),str(lbpvalue)]
                featureWriter.writerow(rowlist)


# genLBPfeatures()

def drawLBP(featurefile):
    plt.figure(figsize=(20, 15))
    xycoord = ParseXMLDrawROI(xmlfile, 'g', 0.5)

    with open(featurefile, 'r') as readfile:
        readfile.readline()

        rowFile = csv.reader(readfile, delimiter=',')

        xlist = list()
        ylist = list()
        featurelist = list()
        for row in rowFile:

            sldx = int(row[0])
            sldy = int(row[1])
            entropy = float(row[2])

            xlist.append(sldx)
            ylist.append(sldy)
            featurelist.append(entropy)

    # plt.scatter(xlist, ylist, c=featurelist, alpha=0.5, cmap='gray')

    imgshape = np.shape(dicomImage)
    print imgshape
    shapey = imgshape[0]
    shapex = imgshape[1]

    z = np.zeros((shapex, shapey))

    for i in range(len(xlist)):
        xc = xlist[i]
        yc = ylist[i]

        pc = featurelist[i]

        inorout = point_inside_polygon(xc, yc, xycoord)

        # if inside plot, set it to p value, if not, set it 0
        z[xc][yc] = pc

        # if inorout == True:
        #     z[xc][yc] = pc
        # else:
        #     z[xc][yc] = 0

    # ParseXMLDrawROI(xmlfile, 'g', 0.5)

    # fill in other pixels which are not in features list
    for otherx in range(2500,3327):
        for othery in range(400,4000):
            z[otherx][othery] = 8

    for otherx in range(0,3327):
        for othery in range(0,400):
            z[otherx][othery] = 8

    for otherx in range(0,3327):
        for othery in range(4000,4095):
            z[otherx][othery] = 8

    plt.imshow(np.transpose(z), alpha= 0.7, cmap='gray')  # change interpolation: "bilinear"
    plt.colorbar()
    # plt.imshow(dicomImage, alpha = 0.8, cmap='gray')

    title = 'Pt9 LE CC LBP FeatureMap Stride3'
    plt.title(title)
    plt.savefig(featureDir + title + '.png', bbox_inches='tight')

    # plt.show()
    plt.cla()
    plt.close()


featurefile = '/Users/yanzhexu/Desktop/Research/featureMap/Pt9_LBPfeatures_onlycenter_s3.csv'

drawLBP(featurefile)

