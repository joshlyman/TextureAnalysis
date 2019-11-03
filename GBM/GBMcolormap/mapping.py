import os
import csv
import fnmatch
import numpy
import SimpleITK
import matplotlib.pyplot as plt

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'

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

        slicenum = slicefile.replace('slice','')
        print slicenum

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
