# Y2 value from Hyunsoo

import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import SimpleITK
import fnmatch
import xml.etree.ElementTree as ET


#rootDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/ColorMap_0302/Prediction'

rootDir = '/Users/yanzhexu/Desktop/Research/Nathan_1008/slicePredictFiles/EGFR/SlicePredictFiles'
dcmDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'
#imgpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/ColorMap_0302/ColorMap_Y2_0302/'
# imgpath = '/Users/yanzhexu/Desktop/Prediction_023117/Prediction new/Colormaps_size3/'

imgpath = '/Users/yanzhexu/Desktop/Research/Nathan_1008/slicePredictFiles/TP53/BrainMaps/opacity_0.2/'
#TrueYDir = 'E:\Documents\AMIIL\AMIIL Papers\Network Constrained Regularization\generate color maps\Comparion.csv'

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
    print predictionfile
    slicename = predictionfile.split('_')[1]
    # print slicename
    slicenum = slicename.replace('slice','')

    predictiondict[ptsname+'_'+slicenum] = predictionfile


# get predict value from prediction file
def generatexyp(predictionfile,contourpts):
    predfile = os.path.join(rootDir,predictionfile)

    with open(predfile, 'r') as predictFile:
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')

        xlist = list()
        ylist = list()
        plist = list()
        biopsylist = list()

        for row in rowFile:
            xc = int(row[0])
            yc = int(row[1])
            pc = float(row[5])

            if point_inside_polygon(xc, yc, contourpts) == True:
                xlist.append(xc)
                ylist.append(yc)
                biopsylist.append(int(row[3]))
                plist.append(pc)

    return xlist,ylist,biopsylist,plist

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

        xyc = list()
        xycoordlist.append(xyc)
        xyc.append(xc)
        xyc.append(yc)

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

    for texturemapfile in os.listdir(dcmDir):
        if texturemapfile.startswith('.'):
            continue
        if texturemapfile.startswith('..'):
            continue

        print texturemapfile

        patientname = texturemapfile.split('_')[0]
        if fnmatch.fnmatch(patientname,"*FSL*"):
            newpatientname = patientname.replace("FSL","")
        elif fnmatch.fnmatch(patientname,"*h*"):
            newpatientname = patientname.replace("h","")
        else:
            newpatientname = patientname
        print newpatientname

        slicepathfile = os.path.join(dcmDir,texturemapfile)

        # newpatientname = 'CE'
        # slicefile = 'slice22'
        # slicenum = '22'

        for slicefile in os.listdir(slicepathfile):
            if slicefile.startswith('.'):
                continue
            if slicefile.startswith('..'):
                continue

            print slicefile

            slicenum = slicefile.replace('slice','')
            print slicenum


            if newpatientname =='CG' and slicefile =='slice37':
                continue

            # get prediction file from prediction dict
            slicepredictfile = predictiondict[newpatientname+'_'+slicenum]
            # print slicepredictfile

            # print xlist
            # print biopsylist
            #
            # get dcm and xml file path
            dcmxmlfilepath = os.path.join(slicepathfile,slicefile)

            for xmlfile in os.listdir(dcmxmlfilepath):
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


            for dcmfile in os.listdir(dcmxmlfilepath):
                if not fnmatch.fnmatch(dcmfile, '*.dcm'):
                    continue


                if fnmatch.fnmatch(dcmfile, '*C*SPGR*') or fnmatch.fnmatch(dcmfile, '*+C*T1*') or fnmatch.fnmatch(
                        dcmfile, '*T1*+C*'):
                    T1dcmfile = dcmfile

                    print T1dcmfile

                if fnmatch.fnmatch(dcmfile, '*T2*'):
                    T2dcmfile = dcmfile

                    print T2dcmfile

                    print '\n'


            dcmfilepath = os.path.join(dcmxmlfilepath,T1dcmfile)
            dicomImage = Read2DImage(dcmfilepath)

            #T2xmlpath = os.path.join(dcmxmlfilepath,T2xmlfile)

            T1xmlpath = os.path.join(dcmxmlfilepath,T1xmlfile)

            plt.figure(figsize= (18,13))

            cm = plt.cm.get_cmap('cool')

            contour = ParseXMLDrawROI(T1xmlpath, 'b', 0.5)

            xlist, ylist, biopsylist, plist = generatexyp(slicepredictfile,contour)

            plt.scatter(xlist, ylist, c=plist, vmin=0, vmax=1, cmap=cm,alpha= 0.05)

            #trueylist = genptlist(TrueYDir)

            # mark biopsy box in colormap and note biopsy number
            # bionum = 0
            # for i in range(len(biopsylist)):
            #     bio = int(biopsylist[i])
            #
            #     if bio == 1:
            #         #print 'found'
            #         bionum += 1
            #         biox = int(xlist[i])
            #         bioy = int(ylist[i])
            #         biopvalue = float(plist[i])
            #
            #         print biox, bioy
            #
            #         # change here to make biopsy true value to prediction value
            #         #dictrow = str(newpatientname) + '_' + str(slicenum) + '_' + str(biox) + '_' + str(bioy)
            #         #truey = trueylist[dictrow]
            #         biopvalue = int((biopvalue * 100) + 0.5) / 100.0
            #         # biop = int(biopvalue * 100)
            #         #plt.scatter(biox, bioy, s=210, facecolor='none', edgecolors='m')
            #         plt.scatter(biox, bioy, c=biopvalue,s=200,  edgecolors='m',linewidths= 3,vmin=0, vmax=1, cmap=cm)
            #
            #         # drawbox(biox, bioy, 'm.-', 3)
            #         # plt.plot (biox, bioy, 'm+')
            #
            #
            #         # plt.text(200, 45 + 10 * bionum, str(biop) + '%', fontsize=25, color='magenta')
            #         # plt.annotate('', xy=(biox, bioy), xytext=(200, 45 + 10 * bionum),
            #         #              arrowprops=dict(facecolor='magenta', width=2, shrink=0.04))

            #ParseXMLDrawROI(T1xmlpath,'m.-',3)

            plt.colorbar()
            plt.imshow(dicomImage,cmap='gray')

            # plt.title(newpatientname + ' ' + ' ' + slicefile + ' T2 Y2', fontsize=30)
            plt.title(newpatientname + ' ' + ' ' + slicefile, fontsize=30)
            #print 1
            # plt.savefig(imgpath + newpatientname +' '+ ' '+ slicefile + ' T2' + ' Y2.png')
            plt.savefig(imgpath + newpatientname + ' ' + ' ' + slicefile+'.png')
            plt.cla()
            plt.close()


generate2Predictplot(dcmDir)
