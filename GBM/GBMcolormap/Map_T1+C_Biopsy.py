# Map all slice folder and get only T1+C ROI with biopsy location and store into folder

import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK


rootDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Prediction'

# old folder: Hu Data Tumor Masks_V3
# new folder: Hu Data Tumor Masks

imgpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/Hu Data Tumor Masks_V3/'
# imgpath = '/Users/yanzhexu/Dropbox/Hu Data Tumor Masks/'

# get PI value from matlab file
dcmDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/'

# biopsy true value
TrueYDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Comparion.csv'


outputfolder = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/ColorMap_T1+C_0820/'
# outputfolder = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/test0322/'
#outputfolder = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/ColorMap_PI_Andrea_0322/'
#outputfolder = '/Users/yanzhexu/Desktop/checkN/yxs-1map/'

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

# store mapping patients folder name in ptsdict
ptsdict = dict()
for ptsfolder in os.listdir(imgpath):
    if ptsfolder.startswith('.'):
        continue
    if ptsfolder.startswith('..'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*Icon*'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*README*'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*HU_PI_Analysis*'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*csv'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*xlsx'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*Validation*'):
        continue

    print ptsfolder

    patientname = ptsfolder.split('_')[0]
    if fnmatch.fnmatch(patientname, "*FSL*"):
        newpatientname = patientname.replace("FSL", "")
    elif fnmatch.fnmatch(patientname, "*h*"):
        newpatientname = patientname.replace("h", "")
    else:
        newpatientname = patientname
    print newpatientname

    ptsfolderpath = os.path.join(imgpath,ptsfolder)

    for T2matfile in os.listdir(ptsfolderpath):
        if T2matfile.startswith('.'):
            continue
        if T2matfile.startswith('..'):
            continue
        if fnmatch.fnmatch(T2matfile, '*Icon*'):
            continue
        if fnmatch.fnmatch(T2matfile,'*T2*mat'):
            T2mat = T2matfile
            print T2mat

    T2matfilepath = ptsfolder+'/'+T2mat
    ptsdict[newpatientname] = T2matfilepath


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


# get sliding window coordinates from prediction file
def generatexyp(predictionfile):
    predfile = os.path.join(rootDir,predictionfile)

    with open(predfile, 'r') as predictFile:
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')

        xlist = list()
        ylist = list()
        biopsylist = list()
        for row in rowFile:
            xlist.append(int(row[0]))
            ylist.append(int(row[1]))
            biopsylist.append(int(row[3]))

    return xlist,ylist,biopsylist


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



def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


def generatePlist(xlist,ylist,newpatientname,slicenum):
    ptsfolder = ptsdict[newpatientname]
    T2matfile = os.path.join(imgpath, ptsfolder)

    T2mat = sio.loadmat(T2matfile)
    T2array = T2mat['u']

    T2size = np.shape(T2array)
    print 'T2 array size:',T2size

    plist = list()
    for i in range(len(xlist)):
        x = xlist[i]
        y = ylist[i]
        # in matlab, coordinate is larger than python for 1 pixel, they give slicenum, we define the x and y,
        # T2array starts from 0 after being imported
        pvalue = T2array[y,x,slicenum-1]
        plist.append(pvalue)

    return plist

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
def generate6Predictplot(dcmDir):

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

            # get x,y list (sliding window coordinates) from prediction folder
            xlist,ylist,biopsylist = generatexyp(slicepredictfile)

            # get plist from Hu data dict
            # plist = generatePlist(xlist,ylist,newpatientname,int(slicenum))

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

            # change T2 dcm file to T1 dcm file
            dcmfilepath = os.path.join(dcmxmlfilepath,T1dcmfile)
            dicomImage = Read2DImage(dcmfilepath)

            # T2xmlpath = os.path.join(dcmxmlfilepath,T2xmlfile)

            T1xmlpath = os.path.join(dcmxmlfilepath,T1xmlfile)

            plt.figure(figsize= (18,13))
            #plt.figure()

            # cm = plt.cm.get_cmap('jet')
            # plt.scatter(xlist, ylist, c=plist,vmin = 0, vmax =1,cmap = cm)

            trueylist = genptlist(TrueYDir)

            # mark biopsy box in colormap and note biopsy number
            bionum = 0
            for i in range(len(biopsylist)):
                bio = int(biopsylist[i])

                if bio ==1:
                    bionum +=1
                    biox = int(xlist[i])
                    bioy = int(ylist[i])

                    print biox,bioy

                    dictrow = str(newpatientname) + '_'+str(slicenum) + '_' + str(biox)+'_'+str(bioy)
                    truey = trueylist[dictrow]

                    truey =int(truey*100)

                    drawbox(biox,bioy,'m.-',3)
                    plt.plot(biox,bioy,'m+')
                    plt.text(200,45+10*bionum, str(truey)+'%',fontsize = 25,color='magenta')
                    plt.annotate('',xy=(biox, bioy),xytext = (200,45+10*bionum),arrowprops=dict(facecolor='magenta', width=2, shrink=0.04))

            # ParseXMLDrawROI(T2xmlpath,'b',0.5)
            ParseXMLDrawROI(T1xmlpath,'m.-',3)

            # plt.colorbar()
            plt.imshow(dicomImage,cmap='gray')

            plt.title(newpatientname +' '+ ' '+ slicefile + ' T1',fontsize = 30)

            plt.savefig(outputfolder + newpatientname +' '+ ' '+ slicefile + ' T1.png')
            plt.cla()
            plt.close()


generate6Predictplot(dcmDir)