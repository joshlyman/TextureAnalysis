import scipy.io as sio
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import fnmatch
import SimpleITK


T1Dir = '/Users/yanzhexu/Dropbox/Hu Data Tumor Masks/'
#T1Dir = '/Users/yanzhexu/Dropbox/Hu Data Tumor Masks/VBr_HU0004/T1Gd/T1Gd.mat'
#T1woNDir = '/Users/yanzhexu/Dropbox/Hu Data Tumor Masks/VBr_HU0004/T1Gd/T1Gd_woT0.mat'

# coordDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Andrea PI Prediction 0322/VBr slice18.csv'
coordDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Andrea PI Prediction 0322'


coordNDir='/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/GBMNecurfiles/NecrosisValue'
coordNImagesDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/GBMNecurfiles/NecursosisImages/'

#coordNDir='/Users/yanzhexu/Desktop/checkN/yxs-1N'
#coordNImagesDir = '/Users/yanzhexu/Desktop/checkN/yxs-1values/'

# T1dcmDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/VBrFSL_slices_only/slice18/+C_Ax_T1_MP_SPGR_IM-0004-0018.dcm'
T1dcmDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/'

# draw rectangle plot (whole rectangle and each ROI box)
def drawplot(contourx1,contourx2,contoury1,contoury2,color,width):
    plt.plot([contourx1, contourx1], [contoury1, contoury2], color,width)
    plt.plot([contourx1, contourx2], [contoury1, contoury1], color,width)
    plt.plot([contourx1, contourx2], [contoury2, contoury2], color,width)
    plt.plot([contourx2, contourx2], [contoury1, contoury2], color,width)

# draw each ROI box
def drawbox(xcoord,ycoord,color,width):
    localx1 = xcoord - 0.5
    localx2 = xcoord + 0.5
    localy1 = ycoord - 0.5
    localy2 = ycoord + 0.5
    drawplot(localx1, localx2, localy1, localy2, color,width)

# read 2D dicom image
def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


def writetwovalueonfile(T1GdwoT0path, T1Gdpath,newpatientname, slicenum,newfile):

    T1mat = sio.loadmat(T1Gdpath)
    T1noNmat = sio.loadmat(T1GdwoT0path)

    T1array = T1mat['T1Gd']
    T1arraynoN = T1noNmat['T1Gd_woT0']

    newfilepath = os.path.join(coordDir,newfile)

    with open(newfilepath, 'r') as predictFile:
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')

        xlist = list()
        ylist = list()
        plist = list()
        for row in rowFile:
            xlist.append(int(row[0]))
            ylist.append(int(row[1]))
            plist.append(float(row[2]))

    T1list = list()
    T1woNlist = list()

    for i in range(len(xlist)):
        x = xlist[i]
        y = ylist[i]
        T1value = T1array[y, x, slicenum-1]
        T1woNvalue = T1arraynoN[y, x, slicenum-1]

        T1list.append(T1value)
        T1woNlist.append(T1woNvalue)

    featuresOutFn = '.csv'

    Necurfeatures = coordNDir+'/' + newpatientname+' slice'+str(slicenum)+'Necur'+ featuresOutFn

    featureTitle = ['X', 'Y', 'PI', 'T1', 'T1woN','Necrosis']

    with open(Necurfeatures, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')
        featureWriter.writerow(featureTitle)

        for i in range(len(xlist)):
            x = xlist[i]
            y = ylist[i]
            p = plist[i]
            T1 = int(T1list[i])
            T1woN = int(T1woNlist[i])

            if T1 == 1 and T1woN == 0:
                Necros = 1
            else:
                Necros = 0

            row = list()
            row.append(x)
            row.append(y)
            row.append(p)
            row.append(T1)
            row.append(T1woN)
            row.append(Necros)

            featureWriter.writerow(row)
    return Necurfeatures


for ptsfolder in os.listdir(T1dcmDir):
    if ptsfolder.startswith('.'):
        continue
    if ptsfolder.startswith('..'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*Icon*'):
        continue

    patientname = ptsfolder.split('_')[0]
    if fnmatch.fnmatch(patientname, "*FSL*"):
        newpatientname = patientname.replace("FSL", "")
    elif fnmatch.fnmatch(patientname, "*h*"):
        newpatientname = patientname.replace("h", "")
    else:
        newpatientname = patientname
    print newpatientname

    newpatientnamepath = os.path.join(T1dcmDir,ptsfolder)


    for ptsf2 in os.listdir(T1Dir):
        if ptsf2.startswith('.'):
            continue
        if ptsf2.startswith('..'):
            continue
        if fnmatch.fnmatch(ptsf2, '*Icon*'):
            continue

        patientname = ptsf2.split('_')[0]

        if fnmatch.fnmatch(patientname,'*'+newpatientname+'*'):
            ptsf2path = os.path.join(T1Dir,ptsf2)

            T1path = os.path.join(ptsf2path,'T1Gd')
            T1GdwoT0path = os.path.join(T1path,'T1Gd_woT0.mat')
            T1Gdpath = os.path.join(T1path,'T1Gd.mat')


            for slicefolder in os.listdir(newpatientnamepath):
                if slicefolder.startswith('.'):
                    continue
                if slicefolder.startswith('..'):
                    continue
                if fnmatch.fnmatch(slicefolder, '*Icon*'):
                    continue

                slicenum = int(slicefolder.split('slice')[1])

                if newpatientname =='CG' and slicenum ==37:
                    continue

                newfile = newpatientname + ' slice' + str(slicenum) + '.csv'
                newfilepath = writetwovalueonfile(T1GdwoT0path, T1Gdpath,newpatientname,slicenum,newfile)
                # featuresOutFn = '.csv'
                #
                # Necurfeatures = coordNDir + '/' + newpatientname + ' slice' + str(slicenum) + 'Necur' + featuresOutFn
                #
                # slicefolderpath = os.path.join(newpatientnamepath,slicefolder)
                #
                # for dcmfile in os.listdir(slicefolderpath):
                #     if not fnmatch.fnmatch(dcmfile,'*dcm*'):
                #         continue
                #     if fnmatch.fnmatch(dcmfile, '*C*SPGR*') or fnmatch.fnmatch(dcmfile, '*+C*T1*') or fnmatch.fnmatch(dcmfile, '*T1*+C*'):
                #         T1dcmage = os.path.join(slicefolderpath,dcmfile)
                #
                # plt.figure()
                # dicomImage = Read2DImage(T1dcmage)
                #
                # with open(Necurfeatures, 'r') as predictFile:
                #     predictFile.readline()
                #     rowFile = csv.reader(predictFile, delimiter=',')
                #
                #     for row in rowFile:
                #         x = int(row[0])
                #         y = int(row[1])
                #         T1 = int(row[3])
                #         #print T1
                #         T1woN = int(row[4])
                #
                #         if T1 == 1 and T1woN == 0:
                #             plt.plot(x,y,'r+')
                #
                # plt.imshow(dicomImage, cmap='gray')
                # plt.title(newpatientname + ' slice'+str(slicenum)+'T0 Necrosis')
                #
                # plt.savefig(coordNImagesDir+newpatientname + ' slice'+str(slicenum)+'T0 Necrosis.png')
                # plt.cla()
                # plt.close()
                # #









