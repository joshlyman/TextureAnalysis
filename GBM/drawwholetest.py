# draw all 18 pts ROI on dicom image for Dr. Hu to check
# VBr only has 1 roi file (T2) and no T1


import os
import csv
import fnmatch
import numpy
import SimpleITK
import matplotlib.pyplot as plt
import ParseXML

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'
outputDir = '/Users/yanzhexu/Desktop/Research/GBM/T1T2check/'

def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray

for texturemapfile in os.listdir(rootDir):

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

    slicepathfile = os.path.join(rootDir,texturemapfile)

    for slicefile in os.listdir(slicepathfile):
        if slicefile.startswith('.'):
            continue
        if slicefile.startswith('..'):
            continue

        print slicefile


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


        T1xmlfilepath = os.path.join(dcmxmlfilepath,T1xmlfile)
        T2xmlfilepath = os.path.join(dcmxmlfilepath,T2xmlfile)
        T1dcmfilepath = os.path.join(dcmxmlfilepath,T1dcmfile)
        T2dcmfilepath = os.path.join(dcmxmlfilepath,T2dcmfile)


        # original image T1
        plt.figure()
        T1dicomImage = Read2DImage(T1dcmfilepath)
        plt.imshow(T1dicomImage, cmap='gray')
        ParseXML.ParseXMLDrawROI(T1xmlfilepath)
        plt.title(newpatientname +' '+ ' '+slicefile + ' T1')
        plt.savefig(outputDir+newpatientname +' '+ ' '+ slicefile + ' T1.png')
        plt.cla()
        plt.close()

        # original image T2
        plt.figure()
        T2dicomImage = Read2DImage(T2dcmfilepath)
        plt.imshow(T2dicomImage, cmap='gray')
        ParseXML.ParseXMLDrawROI(T2xmlfilepath)
        plt.title(newpatientname +' '+ ' '+ slicefile + ' T2')
        plt.savefig(outputDir+newpatientname +' '+ ' '+ slicefile + ' T2.png')
        plt.cla()
        plt.close()


