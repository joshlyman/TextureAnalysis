import os
import numpy
import csv
import fnmatch

filepath ='/Users/yanzhexu/Desktop/Research/HCC/HCCVariant (MR - Al)'

fileout = '/Users/yanzhexu/Desktop/Research/HCC/HCC_Out/Box_size_Lesion.csv'
#fileout = '/Users/yanzhexu/Desktop/Research/HCC/HCC_Out/Box_size_Normal.csv'


casenum = 0
phasenum = 0
largestboxnum = 0

featureTitle = ['PatientID' ,'Phase', 'Width', 'Height']
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

        casenum +=1
        print casefile


        patientid = casefile.split('_')[1] + casefile.split('_')[2]


        splitlist = casefile.split('_')

        phasename = ''
        for item in splitlist[3:len(splitlist)]:
            phasename = phasename +' '+item

        print patientid
        print phasename

        phasefilepath = os.path.join(filepath,casefile)

        lesionfolder = []
        normalfolder = []

        for phasefile in os.listdir(phasefilepath):
            if phasefile.startswith('.'):
                continue
            if phasefile.startswith('..'):
                continue
            if fnmatch.fnmatch(phasefile, '*Icon*'):
                continue
            if fnmatch.fnmatch(phasefile,'*Lesion*') or fnmatch.fnmatch(phasefile,'*lesion*'):
                lesionfolder.append(phasefile)
            if fnmatch.fnmatch(phasefile,'*Normal_Liver*') or fnmatch.fnmatch(phasefile,'*Normal_Liver*') or fnmatch.fnmatch(phasefile,'*liver*'):
                normalfolder.append(phasefile)


        lesionnormpair = []
        print lesionfolder
        print normalfolder

        for lesionitem in lesionfolder:
            if fnmatch.fnmatch(lesionitem,'Lesion'):
                lesionnormpair.append(['Lesion','Normal_Liver'])
                normalfolder.remove('Normal_Liver')
            else:
                if fnmatch.fnmatch(lesionitem,'*Lesion*'):
                    matchitem = lesionitem.replace('Lesion','')
                else:
                    matchitem = lesionitem.replace('lesion','')

                for normalitem in normalfolder:

                    if fnmatch.fnmatch(normalitem, '*Normal_Liver*'):
                        matchitem2 = normalitem.replace('Normal_Liver', '')
                    else:
                        matchitem2 = normalitem.replace('liver', '')

                    if matchitem == matchitem2:
                        lesionnormpair.append([lesionitem,normalitem])


        print lesionnormpair





                # phasenum +=1
            # print phasefile
            #
            #
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
            #                 aFeature = [patientid,phasename, aROI['W'], aROI['H']]
            #
            #                 featureWriter.writerow(aFeature)









# print min(aROIW),max(aROIW)
# print min(aROIH),max(aROIH)
# print largestboxnum
#print casenum
# print phasenum