# updated Raw Mean and Std based on whole image normalization (Max and Min)

import os
import csv
import fnmatch
import SimpleITK
import numpy

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'

texturesPath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addYlabel/GBM_SlidingWindow_TextureMap'

outputpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/AddGlobalNormedRawMeaninside/'

# outputpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/TestWithoutNorm/'


def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


def Norm_Mean_Std_LargestBox(imgArray,imgMax,imgMin):

    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    meang = numpy.mean(imgArray)
    stdg = numpy.std(imgArray)

    return meang,stdg

for texturesfile in os.listdir(texturesPath):
    if texturesfile.startswith('.'):
        continue
    if texturesfile.startswith('..'):
        continue

    print texturesfile

    patient = texturesfile.split('_')[0]
    slicenum = texturesfile.split('_')[1].split('slice')[1]

    texturesfilepath = os.path.join(texturesPath,texturesfile)

    for casefolder in os.listdir(rootDir):
        if casefolder.startswith('.'):
            continue

        if casefolder.startswith('..'):
            continue

        if fnmatch.fnmatch(casefolder,'*'+str(patient)+'*'):
            print casefolder

            print '\n'


            slicefolder = 'slice'+str(slicenum)
            casefolderpath = os.path.join(rootDir,casefolder)
            slicefolderpath = os.path.join(casefolderpath,slicefolder)

            dcmfiledict = dict()
            for dcmfile in os.listdir(slicefolderpath):

                if dcmfile.startswith('.'):
                    continue
                if fnmatch.fnmatch(dcmfile, '*dcm*') is False:
                    continue
                if fnmatch.fnmatch(dcmfile, '*precontrast*'):
                    continue

                if fnmatch.fnmatch(dcmfile, '*C*SPGR*') or fnmatch.fnmatch(dcmfile, '*+C*T1*') or fnmatch.fnmatch(
                        dcmfile, '*T1*+C*'):
                    SPGRCfile = dcmfile
                    dcmfiledict['SPGRC'] = SPGRCfile

                if fnmatch.fnmatch(dcmfile, '*T2*'):
                    T2file = dcmfile
                    dcmfiledict['T2'] = T2file

                if fnmatch.fnmatch(dcmfile, '*q*'):
                    Qfile = dcmfile
                    dcmfiledict['Q'] = Qfile

                if fnmatch.fnmatch(dcmfile, '*p*'):
                    Pfile = dcmfile
                    dcmfiledict['P'] = Pfile

                if fnmatch.fnmatch(dcmfile, '*rCBV*'):
                    RCBVfile = dcmfile
                    dcmfiledict['RCBV'] = RCBVfile

                if fnmatch.fnmatch(dcmfile, '*EPI*+C*') or fnmatch.fnmatch(dcmfile, '*+C*EPI*'):
                    EPIfile = dcmfile
                    dcmfiledict['EPI'] = EPIfile


            outputfeaturefilepath = os.path.join(outputpath,texturesfile)

            with open(outputfeaturefilepath, 'wb') as writefile:
                featureWriter = csv.writer(writefile, dialect='excel')

                with open(texturesfilepath, 'r') as featuresfile:
                    # featuresfile.readline()
                    rowFile = csv.reader(featuresfile, delimiter=',')

                    for row in rowFile:
                        if row[0] == 'Image Contrast':
                            row.insert(42,'Global Normalized Raw Mean')
                            row.insert(43,'Global Normalized Raw Std')

                            featureWriter.writerow(row)
                        else:
                            contrast = row[0]
                            dcmfile = dcmfiledict[contrast]
                            dcmfilepath = os.path.join(slicefolderpath,dcmfile)


                            xcoord = int(row[2])
                            ycoord = int(row[3])

                            dicomImage = Read2DImage(dcmfilepath)

                            subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]
                            Raw_mean, Raw_std = Norm_Mean_Std_LargestBox(subImage, dicomImage.max(), dicomImage.min())


                            row.insert(42,Raw_mean)
                            row.insert(43,Raw_std)

                            featureWriter.writerow(row)










