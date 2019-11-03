import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET
from matplotlib import cm


rootDir = '/Users/yanzhexu/Dropbox/Prediction/VBr_slice18_T2_ROI_Texture_Map_PredictY6.csv'
dcmDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/VBrFSL_slices_only/slice18/'
imgpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/'


with open(rootDir, 'r') as roiFile:
    roiFile.readline()

    rowFile = csv.reader(roiFile, delimiter=',')

    xlist = list()
    ylist = list()
    p2list = list()
    for row in rowFile:
        xlist.append(int(row[0]))
        ylist.append(int(row[1]))
        p2list.append(float(row[6]))


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

    plt.plot(xcoordlist,ycoordlist,color,linewidth = width )


def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


dcmfile = 'Ax_T2_FSE_IM-0001-0018.dcm'
dcmfilepath = os.path.join(dcmDir,dcmfile)
dicomImage = Read2DImage(dcmfilepath)

T2xml = 'VB_ROI_Ax T2 FSE INTER (registered) (RESEARCH).xml'
T2xmlpath = os.path.join(dcmDir,T2xml)

T1xml = 'VB_ROI_+C_Ax_T1_MP_SPGR_IM-0004-0018.xml'
T1xmlpath = os.path.join(dcmDir,T1xml)

plt.figure(figsize= (18,13))
#plt.figure()

plt.scatter(xlist, ylist, c=p2list,vmin = 0, vmax =1)


ParseXMLDrawROI(T2xmlpath,'b',0.5)
ParseXMLDrawROI(T1xmlpath,'m.-',3)

plt.colorbar()
plt.imshow(dicomImage,cmap='gray')

plt.title('VBr slice18 T2_Y6')
plt.show()

#plt.savefig(imgpath + 'VBr slice18 T2 Y6.png')
plt.cla()
plt.close()