import os
import numpy
import csv
import fnmatch

filepath ='/Users/yanzhexu/Desktop/Research/Prostate/Output'

#fileout = '/Users/yanzhexu/Desktop/Research/Prostate_Out/Box_size_Lesion.xlsx'
fileout = '/Users/yanzhexu/Desktop/Research/Prostate_Out/Box_size_Control.csv'


casenum = 0
phasenum = 0
largestboxnum = 0

featureTitle = ['Patient' , 'Width', 'Height']
aROIW = list()
aROIH = list()
# with open(fileout, 'wb') as featureCSVFile:
#     featureWriter = csv.writer(featureCSVFile, dialect='excel')
#     featureWriter.writerow(featureTitle)

for casefile in os.listdir(filepath):
    if casefile.startswith('.'):
        continue
    if casefile.startswith('..'):
        continue
    if fnmatch.fnmatch(casefile, '*Icon*'):
        continue
    casenum +=1
    print casefile

    if fnmatch.fnmatch(casefile,'*20160212*'):
        phaseid = '20160212'
    else:
        phaseid = casefile.split('_')[2]

    if fnmatch.fnmatch(casefile,'*ADC*'):
        phasename = 'ADC'
    elif fnmatch.fnmatch(casefile,'*TRACEW*'):
        phasename= 'TRACEW'
    else:
        phasename = 'FOV'

    print phaseid
    print phasename





        # phasefilepath = os.path.join(filepath,casefile)
        #
        # for phasefile in os.listdir(phasefilepath):
        #     if phasefile.startswith('.'):
        #         continue
        #     if phasefile.startswith('..'):
        #         continue
        #     if fnmatch.fnmatch(phasefile, '*Icon*'):
        #         continue
        #     if fnmatch.fnmatch(phasefile,'Lesion'):
        #         continue
        #
        #     phasenum +=1
        #     print phasefile


            # roipath = os.path.join(phasefilepath,phasefile)
            # for roifile in os.listdir(roipath):
            #     if roifile.startswith('.'):
            #         continue
            #     if roifile.startswith('..'):
            #         continue
            #     if fnmatch.fnmatch(roifile, '*Icon*'):
            #         continue
            #     if fnmatch.fnmatch(roifile,'*rec.csv'):
            #         largestboxfile = roifile
            #         print largestboxfile
            #
            #         largestboxnum +=1
            #
            #         recpath = os.path.join(roipath,largestboxfile)
            #
            #         with open(recpath, 'r') as roiFile:
            #             roiList = csv.DictReader(roiFile, dialect='excel')
            #             for aROI in roiList:
            #                 aROIW.append(int(aROI['W']))
            #                 aROIH.append(int(aROI['H']))
            #                 aFeature = [casefile, aROI['W'], aROI['H']]
            #
            #                 featureWriter.writerow(aFeature)









# print min(aROIW),max(aROIW)
# print min(aROIH),max(aROIH)
# print largestboxnum
print casenum
# print phasenum