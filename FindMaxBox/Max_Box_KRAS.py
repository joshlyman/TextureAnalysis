import os
import numpy
import csv
import fnmatch

filepath ='/Users/yanzhexu/Desktop/Research/KRAS/Feb. 2017'

fileout = '/Users/yanzhexu/Desktop/Research/KRAS/KRAS_Box_size_Control.csv'


casenum = 0
phasenum = 0
largestboxnum = 0

featureTitle = ['Patient','X','Y','Width', 'Height']
aROIX = list()
aROIY = list()
aROIW = list()
aROIH = list()


with open(fileout, 'wb') as featureCSVFile:
    featureWriter = csv.writer(featureCSVFile, dialect='excel')
    featureWriter.writerow(featureTitle)

    for casefile in os.listdir(filepath):
        if casefile.startswith('.'):
            continue
        if casefile.startswith('..'):
            continue
        if fnmatch.fnmatch(casefile, '*Icon*'):
            continue

        if fnmatch.fnmatch(casefile,'*xlsx*'):
            continue

        casenum +=1
        print casefile

        patientID = casefile
        print patientID

        patientfilepath = os.path.join(filepath,casefile)

        lesionDir = list()
        normalDir = list()

        for patientPhaseDir in os.listdir(patientfilepath):
            if patientPhaseDir.startswith('.'):
                continue
            if patientPhaseDir.startswith('..'):
                continue
            if fnmatch.fnmatch(patientPhaseDir, '*Icon*'):
                continue

            if fnmatch.fnmatch(patientPhaseDir, '*Lesion*'):
                lesionDir.append(patientPhaseDir)

                print lesionDir

            if fnmatch.fnmatch(patientPhaseDir, '*Control*'):
                normalDir.append(patientPhaseDir)

                print normalDir

        recfile = 'largest_rec.csv'

        # for lesionfolder in lesionDir:
        #     lesionfile = os.path.join(patientfilepath,lesionfolder)
        #     largestrecpath = os.path.join(lesionfile,recfile)
        for normalfolder in normalDir:
            normalfile = os.path.join(patientfilepath, normalfolder)
            largestrecpath = os.path.join(normalfile, recfile)

            with open(largestrecpath, 'r') as roiFile:
                roiList = csv.DictReader(roiFile, dialect='excel')
                for aROI in roiList:

                    aROIX.append(int(aROI['X']))
                    aROIY.append(int(aROI['Y']))
                    aROIW.append(int(aROI['W']))
                    aROIH.append(int(aROI['H']))

                aFeature = [casefile, aROI['X'], aROI['Y'],aROI['W'], aROI['H']]

                featureWriter.writerow(aFeature)

print min(aROIW),max(aROIW)
print min(aROIH),max(aROIH)
# print largestboxnum
print casenum
# print phasenum