import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET
import re

rootDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Prediction'

# get dcm file path
dcmDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/RWh_slices_only/slice17/'

# get image path file
imgpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/ColorMap_Nathan_RWh_0303/'

# get biopsy true density value
TrueYDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Comparion.csv'



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

# get and store predictionfile in dict
predictiondict = dict()
for predictionfile in os.listdir(rootDir):

    if predictionfile.startswith('.'):
        continue
    if predictionfile.startswith('..'):
        continue
    if fnmatch.fnmatch(predictionfile,'*Icon*'):
        continue

    # print predictionfile

    ptsname = predictionfile.split('_')[0]
    slicename = predictionfile.split('_')[1]
    slicenum = slicename.replace('slice','')

    predictiondict[ptsname+'_'+slicenum] = predictionfile


# get predict value from prediction file
def generatexyp(predictionfile):
    predfile = os.path.join(rootDir,predictionfile)

    with open(predfile, 'r') as predictFile:
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')

        xlist = list()
        ylist = list()
        plist = list()
        biopsylist = list()
        for row in rowFile:
            a = re.sub("\D", "", row[0])
            b = re.sub("\D", "", row[1])
            c = re.sub("\D", "", row[2])
            d = row[3]

            if d =="":
                continue
            d = float(d)

            # print a
            # print b
            # print c
            #print d
            # xlist.append(int(row[0]))
            # ylist.append(int(row[1]))
            xlist.append(a)
            ylist.append(b)
            biopsylist.append(c)
            plist.append(d)
            #biopsylist.append(int(row[2]))
            #plist.append(float(row[3]))

    return xlist,ylist,biopsylist,plist


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

# get true Y list from compare file
def genptlist(comparefilepath):
    with open(comparefilepath, 'r') as predictFile:
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')
        trueylist = dict()

        for row in rowFile:
            if row[0] =='':
                continue

            # dict: ptid + slicenum + X + Y
            dictrow = str(row[0])+'_'+str(row[8])+'_' + str(row[9])+'_' + str(row[10])

            trueylist[dictrow] = float(row[11])

    return trueylist

# mapping 18 pts folder for plotting prediction value
def generate2Predictplot(dcmDir):

    newpatientname = 'RW'
    slicefile = 'slice17'
    slicenum = str(17)

    # get prediction file from prediction dict
    #slicepredictfile = predictiondict[newpatientname + '_' + slicenum]
    predictionfile = 'RW slice17_predictions2.csv'

    slicepredictfile = os.path.join(imgpath,predictionfile)

    xlist, ylist, biopsylist,plist = generatexyp(slicepredictfile)


    for xmlfile in os.listdir(dcmDir):
        if not fnmatch.fnmatch(xmlfile, '*.xml'):
            continue

        # NECROSIS is dark area of T1 and need to be used in colourmap analysis (shown in RGr...)
        if fnmatch.fnmatch(xmlfile, '*NECROSIS*'):
            continue

        if fnmatch.fnmatch(xmlfile, '*C*SPGR*') or fnmatch.fnmatch(xmlfile, '*+C*T1*') or fnmatch.fnmatch(
                xmlfile, '*T1*+C*'):
            T1xmlfile = xmlfile
            print T1xmlfile

        if fnmatch.fnmatch(xmlfile, '*T2*'):
            T2xmlfile = xmlfile
            print T2xmlfile

    T2dcmfile  = list()
    for dcmfile in os.listdir(dcmDir):
        if not fnmatch.fnmatch(dcmfile, '*.dcm'):
            continue

        if fnmatch.fnmatch(dcmfile, '*C*SPGR*') or fnmatch.fnmatch(dcmfile, '*+C*T1*') or fnmatch.fnmatch(
                dcmfile, '*T1*+C*'):
            T1dcmfile = dcmfile

            print T1dcmfile

        if fnmatch.fnmatch(dcmfile, '*T2*'):
            T2dcmfile.append(dcmfile)

            print T2dcmfile

            print '\n'

    for eachT2 in T2dcmfile:
        T2dcmfilepath = os.path.join(dcmDir, eachT2)

        dicomImage = Read2DImage(T2dcmfilepath)

        T2xmlpath = os.path.join(dcmDir,T2xmlfile)

        T1xmlpath = os.path.join(dcmDir,T1xmlfile)

        plt.figure(figsize= (18,13))

        cm = plt.cm.get_cmap('jet')
        plt.scatter(xlist, ylist, c=plist, vmin=0, vmax=1, cmap=cm)

        #trueylist = genptlist(TrueYDir)

        # mark biopsy box in colormap and note biopsy number
        # bionum = 0
        # for i in range(len(biopsylist)):
        #     bio = int(biopsylist[i])
        #
        #     if bio == 1:
        #         bionum += 1
        #         biox = int(xlist[i])
        #         bioy = int(ylist[i])
        #
        #         print biox, bioy
        #
        #         dictrow = str(newpatientname) + '_' + str(slicenum) + '_' + str(biox) + '_' + str(bioy)
        #         #truey = trueylist[dictrow]
        #
        #         #truey = int(truey * 100)
        #
        #         drawbox(biox, bioy, 'm.-', 3)
        #         plt.plot(biox, bioy, 'm+')
        #         #plt.text(200, 45 + 10 * bionum, str(truey) + '%', fontsize=25, color='magenta')
        #         # plt.annotate('', xy=(biox, bioy), xytext=(200, 45 + 10 * bionum),
        #         #              arrowprops=dict(facecolor='magenta', width=2, shrink=0.04))

        ParseXMLDrawROI(T2xmlpath,'b',0.5)
        ParseXMLDrawROI(T1xmlpath,'m.-',3)

        plt.colorbar()
        plt.imshow(dicomImage,cmap='gray')

        # to do: change image name by column name
        plt.title(newpatientname + ' ' + ' ' + slicefile + ' T2 PI+ML', fontsize=30)

        # to do: change image name by column name
        plt.savefig(imgpath + newpatientname +' '+ ' '+ slicefile + ' T2 PI+ML' + ' .png')
        plt.cla()
        plt.close()


generate2Predictplot(dcmDir)
