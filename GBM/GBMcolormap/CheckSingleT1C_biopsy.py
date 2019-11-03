# This is for checking single T1+C ROI and biopsy

import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK



dcmDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/'

# SF slice folder
# slicefolder = 'SF_slices_only/slice23/'
# SF
# T1xmlfile = 'roi for +C_Ax_T1_MP_SPGR_IM-0001-0023.xml'
# T1dcmimage = '+C_Ax_T1_MP_SPGR_IM-0001-0023.dcm'

# ET slice folder
# slicefolder = 'ETFSL_slices_only/slice21/'
# T1xmlfile = 'ET_ROI_+C_Ax_T1_MP_SPGR_IM-0002-0021.xml'
# T1dcmimage = '+C_Ax_T1_MP_SPGR_IM-0002-0021.dcm'

# NT slice folder
slicefolder = 'NTFSL_slices_only/slice23/'
# T1xmlfile1 = 'roi for T1+C_3D_AXIAL_IRSPGR_IM-0004-0023.xml'
T1dcmimage = 'T1+C_3D_AXIAL_IRSPGR_IM-0004-0023.dcm'


# T1xmlfilepath1 = dcmDir + slicefolder + T1xmlfile1
T1dcmimagepath = dcmDir + slicefolder + T1dcmimage

# SF slice 23
# BiopsyX = 152
# BiopsyY = 185

# ET slice 21
# BiopsyX = 100
# BiopsyY = 148

# NT slice 23
BiopsyX = 131
BiopsyY = 93

Outputfolder = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/ColorMap_T1+C_0820/CheckSingleCase/'


# 2 ROIs for NT slice 23. 1 is in biopsy and another 1 in the right
T1xmlfile1 = 'NT_slice_23_T1+C_ROI.xml'
T1xmlfilepath1 = Outputfolder + T1xmlfile1

T1xmlfile2 = 'NT_slice_23_T1+C_ROI_next_to_bx.xml'
T1xmlfilepath2 = Outputfolder + T1xmlfile2

# Draw ROI boundary
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

    print xcoordlist
    print ycoordlist

    print len(xcoordlist)
    print len(ycoordlist)

    plt.plot(xcoordlist,ycoordlist,color,linewidth = width)


def drawplot(contourx1,contourx2,contoury1,contoury2,color,width):
    plt.plot([contourx1, contourx1], [contoury1, contoury2], color,width)
    plt.plot([contourx1, contourx2], [contoury1, contoury1], color,width)
    plt.plot([contourx1, contourx2], [contoury2, contoury2], color,width)
    plt.plot([contourx2, contourx2], [contoury1, contoury2], color,width)


# Draw each ROI box
def drawbox(xcoord,ycoord,color,width):
    localx1 = xcoord - 2
    localx2 = xcoord + 2
    localy1 = ycoord - 2
    localy2 = ycoord + 2
    drawplot(localx1, localx2, localy1, localy2, color,width)

# Read dicom image
def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray



plt.figure(figsize=(20,15))

ParseXMLDrawROI(T1xmlfilepath1,'m',1)
ParseXMLDrawROI(T1xmlfilepath2,'m',1)

dicomImage = Read2DImage(T1dcmimagepath)

plt.imshow(dicomImage,cmap='gray')

plt.plot(BiopsyX,BiopsyY,'r+',10)
drawbox(BiopsyX,BiopsyY,'r',3)


# testpoint
# test1X = 112
# test1Y = 166
#
# test2X = 97
# test2Y = 160



# plt.plot(test1X,test1Y,'r+',10)
# plt.plot(test2X,test2Y,'r+',10)

# titlename = 'SF slice23 T1+C with Biopsy'
# titlename = 'ET slice21 T1+C with Biopsy'
titlename = 'NT slice23 T1+C with Biopsy'

plt.title(titlename,fontsize = 30)

outputName = Outputfolder + titlename


plt.savefig(outputName,bbox_inches='tight')
plt.cla()
plt.close()

# plt.show()


