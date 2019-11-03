from pylab import *
import SimpleITK
from matplotlib import pyplot as plt
import numpy as np
import csv
import os
import fnmatch

rootDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/Marley Grant Data'

fileout = '/Users/yanzhexu/Desktop/Research/Marley Grant Data 92/BI_92_Box_size.csv'

recfilenum = 0
aROIW = []
aROIH = []
featureTitle = ['PatientID' ,'Phase', 'Width', 'Height']

with open(fileout, 'wb') as featureCSVFile:
    featureWriter = csv.writer(featureCSVFile, dialect='excel')
    featureWriter.writerow(featureTitle)
    for casefile in os.listdir(rootDir):
        if casefile.startswith('.'):
            continue
        if casefile.startswith('..'):
            continue
        if fnmatch.fnmatch(casefile, '*Icon*'):
            continue
        print '\n'
        print casefile

        patientid = casefile.split('-')[0]

        patientfolderpath = os.path.join(rootDir, casefile)

        for patientfolder in os.listdir(patientfolderpath):
            if patientfolder.startswith('.'):
                continue
            if patientfolder.startswith('..'):
                continue
            if fnmatch.fnmatch(patientfolder, '*Icon*'):
                continue
            if fnmatch.fnmatch(patientfolder, '*roi*'):
                continue

            # print casefile2

            Dfolderpath = os.path.join(patientfolderpath, patientfolder)

            for phasefolder in os.listdir(Dfolderpath):

                phasefolderpath = os.path.join(Dfolderpath, phasefolder)
                if phasefolder.startswith('.'):
                    continue
                if phasefolder.startswith('..'):
                    continue
                if phasefolder.startswith('*Icon*'):
                    continue
                if os.path.isfile(phasefolderpath):
                    continue

                print phasefolder

                phase1 = phasefolder.split('-')[0].replace(' ','')
                if fnmatch.fnmatch(phase1,'*CC*DES*'):
                    phasename = 'CC DES'
                elif fnmatch.fnmatch(phase1,'*CC*LE*'):
                    phasename = 'CC LE'
                elif fnmatch.fnmatch(phase1, '*MLO*DES*'):
                    phasename = 'MLO DES'
                elif fnmatch.fnmatch(phase1,'*MLO*LE*'):
                    phasename = 'MLO LE'
                elif fnmatch.fnmatch(phase1, '*LM*DES*'):
                    phasename = 'LM DES'
                else:
                    phasename = 'LM LE'

                for file in os.listdir(phasefolderpath):

                    if fnmatch.fnmatch(file,'*texture*'):
                        continue
                    if fnmatch.fnmatch(file,'*(1)*'):
                        continue
                    if not fnmatch.fnmatch(file,'*largest_rec*'):
                        continue
                    rectfile = file

                    print file

                    recfilenum +=1

                    recpath = os.path.join(phasefolderpath,file)


                    with open(recpath, 'r') as roiFile:
                        roiList = csv.DictReader(roiFile, dialect='excel')
                        for aROI in roiList:
                            aROIW.append(int(aROI['W']))
                            aROIH.append(int(aROI['H']))
                            aFeature = [patientid,phasename, aROI['W'], aROI['H']]

                            featureWriter.writerow(aFeature)



            # for dcmfile in os.listdir(filename4):
            #     if not fnmatch.fnmatch(dcmfile, '*dcm'):
            #         continue
            #
            #     print dcmfile
print recfilenum
print max(aROIW),min(aROIW)
print max(aROIH),min(aROIH)