#!/usr/bin/env python
#=========================================================================
#
# check Parser path code in GBM code
#
#
#
#=========================================================================

# log
#
#





import os
import csv
import fnmatch
import numpy
import SimpleITK

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'

coorDir = '/Users/yanzhexu/Desktop/Research/GBM/18/patient_biopsy_coordinates_18.csv'

mapDir = '/Users/yanzhexu/Desktop/Research/GBM/18/map between pt numbers and pt label letters.txt'

outputDir = '/Users/yanzhexu/Desktop/Research/GBM/Final_results'

featuresOutFn = 'GBM_features_8*8_18_LBP1.csv'
#featuresOutFn = 'GBM_features_GLCM_test_X_Y_ym4xm4_yp4xp4_3.csv'

# process map data
# get dict for mapping number to letters
mapdict1 = dict()
mapdict2 = dict()
with open(mapDir,'r') as mapFile:
    roiCoordsList = csv.reader(mapFile, delimiter='=')
    for row in roiCoordsList:
        ptnumber = row[0]
        label = row[1]
        mapdict1[ptnumber] = label # get mapdict, such as: 2: RW
        mapdict2[label] = ptnumber # get mapdict, such as: RW:2

num = 0
ptcoordlist = list()

# process coordinate data and get coordinate files
coordinate = list()
ptlist = list()
with open(coorDir, 'r') as roiFile:
    coorList = csv.DictReader(roiFile, dialect='excel')
    for row in coorList:
        num+=1
        coordinate.append(row['Coordinate']) # 161_126_17
        ptlist.append(row['pt_biopsy']) # 2_111622

xydict =  dict()
rowindex = 0
for row in coordinate:
    if fnmatch.fnmatch(row,'*_*'):
        splitrow = row.split('_')
        xydict[rowindex] = list()
        xydict[rowindex].append(int(splitrow[0]))
        xydict[rowindex].append(int(splitrow[1]))
        xydict[rowindex].append(int(splitrow[2]))

    else:
        splitrow = row.split(' ')
        xydict[rowindex] = list()
        xydict[rowindex].append(int(splitrow[0]))
        xydict[rowindex].append(int(splitrow[1]))
        xydict[rowindex].append(int(splitrow[2]))
    rowindex+=1

print 'patientidlist:',xydict
print 'coordinate:',coordinate
print num

# construct mapping from ptname and coordinate data
ptidlist = list()
ptnamelist = list()
for row in ptlist:
    splitrow = row.split('_')
    ptid = splitrow[0]
    ptidlist.append(ptid) # get ptid in list

ptindex = 0
for pt in ptidlist:
    if pt in mapdict1:
        ptname = mapdict1[pt]
        if ptname not in ptnamelist:
            ptnamelist.append(ptname)
        ptcoordlist.append(dict())
        ptcoordlist[ptindex][ptname] = xydict[ptindex]
    else:
        if pt not in ptnamelist:
            ptnamelist.append(pt)
        ptcoordlist.append(dict())
        ptcoordlist[ptindex][pt] = xydict[ptindex]
    ptindex+=1

print 'ptname:',ptnamelist
print 'ptcoordlist:',ptcoordlist
print len(ptcoordlist)


# start to get dicom and process texture

# process slice mapping data
proslice = list()
for patientslice in os.listdir(rootDir):
    if patientslice.startswith('.') or \
            os.path.isfile(os.path.join(rootDir, patientslice)):
        continue
    proslice.append(patientslice)


folderdict = dict() # folder name dict for all pts
proslicelist = list()
for slicename in proslice:
    newslicename = slicename.split('_')[0]
    if fnmatch.fnmatch(newslicename,"*FSL*"):
        newslicename = newslicename.replace("FSL","")
        folderdict[newslicename] = slicename
        proslicelist.append(newslicename)
    elif fnmatch.fnmatch(newslicename,"*h*"):
        newslicename = newslicename.replace("h","")
        folderdict[newslicename] = slicename
        proslicelist.append(newslicename)
    else:
        folderdict[newslicename] = slicename
        proslicelist.append(newslicename)


print 'folderdict',folderdict
print 'proslice',proslice
print len(proslice)
print 'proslicelist',proslicelist
print len(proslicelist)

ptindex = 0
num = 0
for pt in ptnamelist: # such as RW,JTy...according to CSV file to sort

    ptslice = []
    for coordtuple in ptcoordlist:
        if pt in coordtuple:
            ptslice.append(coordtuple[pt])
        #print pt,ptslice
    ptfolderpath = os.path.join(rootDir,folderdict[pt])

    for slicelist in ptslice:
        patientid = ptlist[ptindex]
        ptindex += 1
        slicenum = slicelist[2]
        xcoord = slicelist[0]
        ycoord = slicelist[1]

        slicefolder = 'slice'+ str(slicenum)

        slicefolderpath = os.path.join(ptfolderpath,slicefolder)
        #print pt,slicelist, slicefolderpath

        dcmfiledict = dict()

        for dcmfile in os.listdir(slicefolderpath):

            if dcmfile.startswith('.'):
                continue
            if fnmatch.fnmatch(dcmfile,'*dcm*') is False:
                continue

            if fnmatch.fnmatch(dcmfile,'*C*SPGR*') or fnmatch.fnmatch(dcmfile,'*+C*T1*') or fnmatch.fnmatch(dcmfile,'*T1*+C*'):
                SPGRCfile = dcmfile
                dcmfiledict['SPGRC']=SPGRCfile

            if fnmatch.fnmatch(dcmfile,'*T2*'):
                T2file = dcmfile
                dcmfiledict['T2']=T2file

            if fnmatch.fnmatch(dcmfile,'*q*'):
                Qfile = dcmfile
                dcmfiledict['Q']=Qfile

            if fnmatch.fnmatch(dcmfile,'*p*'):
                Pfile = dcmfile
                dcmfiledict['P'] = Pfile

            if fnmatch.fnmatch(dcmfile,'*rCBV*'):
                RCBVfile = dcmfile
                dcmfiledict['RCBV'] = RCBVfile


            if fnmatch.fnmatch(dcmfile,'*EPI*+C*') or fnmatch.fnmatch(dcmfile,'*+C*EPI*'):
                EPIfile = dcmfile
                dcmfiledict['EPI'] = EPIfile


        print pt,patientid,slicenum,len(dcmfiledict),dcmfiledict
