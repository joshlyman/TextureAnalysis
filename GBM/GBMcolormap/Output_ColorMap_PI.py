import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK


rootDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Prediction'
#imgpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/Hu Data Tumor Masks_V3/'
imgpath = '/Users/yanzhexu/Dropbox/Hu Data Tumor Masks/'

dcmDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/'

# note: if get PI, then use [y,x,slice-1] from matlab files
outputfolder = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Andrea PI Prediction 0322'

#outputfolder = '/Users/yanzhexu/Desktop/checkN/yxs-1PI'

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


# get predict value from prediction file
def generatexyp(predictionfile):
    predfile = os.path.join(rootDir,predictionfile)

    with open(predfile, 'r') as predictFile:
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')

        xlist = list()
        ylist = list()
        for row in rowFile:
            xlist.append(int(row[0]))
            ylist.append(int(row[1]))

    return xlist,ylist


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

    plist = list()
    for i in range(len(xlist)):
        x = xlist[i]
        y = ylist[i]
        # note: if get PI, then use [y,x,slice-1] from matlab files, T2array starts from 0 after being imported
        pvalue = T2array[y,x,slicenum-1]
        plist.append(pvalue)

    return plist

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

            # get x,y list (sliding window) from prediction folder
            xlist,ylist = generatexyp(slicepredictfile)

            # get plist from Hu data dict
            plist = generatePlist(xlist,ylist,newpatientname,int(slicenum))

            featuresOutFn = '.csv'

            T2featuresOutFn = newpatientname + ' ' + slicefile + featuresOutFn
            featuresCSVFn = os.path.join(outputfolder, T2featuresOutFn)

            featureTitle = ['X','Y','PI']


            with open(featuresCSVFn, 'wb') as featureCSVFile:
                featureWriter = csv.writer(featureCSVFile, dialect='excel')
                featureWriter.writerow(featureTitle)

                for i in range(len(xlist)):
                    x = xlist[i]
                    y = ylist[i]
                    p = plist[i]

                    row = list()
                    row.append(x)
                    row.append(y)
                    row.append(p)

                    featureWriter.writerow(row)

generate6Predictplot(dcmDir)