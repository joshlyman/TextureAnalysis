import os
import csv
import fnmatch


rootDir = '/Users/yanzhexu/Desktop/Research/GBM/T1 and T2 texture Maps - grid spacing 4'

coorDir = '/Users/yanzhexu/Desktop/Research/GBM/patient_biopsy_coordinates.csv'

mapDir = '/Users/yanzhexu/Desktop/Research/GBM/map between pt numbers and pt label letters.txt'

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


    slicenum = texturemapfile.split('_')[1].replace('slice','')
    slicenum = int(slicenum)
    print slicenum

    TROI = texturemapfile.split('_')[2]
    print TROI

# folderdict = dict() # folder name dict for all pts
# proslicelist = list()
# for slicename in proslice:
#     newslicename = slicename.split('_')[0]
#     if fnmatch.fnmatch(newslicename,"*FSL*"):
#         newslicename = newslicename.replace("FSL","")
#         folderdict[newslicename] = slicename
#         proslicelist.append(newslicename)
#     elif fnmatch.fnmatch(newslicename,"*h*"):
#         newslicename = newslicename.replace("h","")
#         folderdict[newslicename] = slicename
#         proslicelist.append(newslicename)
#     else:
#         folderdict[newslicename] = slicename
#         proslicelist.append(newslicename)


# print folderdict
# # print proslice
# # print len(proslice)
# print proslicelist

# process map data
# get dict for mapping number to letters


# mapdict1 = dict()
# mapdict2 = dict()
# with open(mapDir,'r') as mapFile:
#     roiCoordsList = csv.reader(mapFile, delimiter='=')
#     for row in roiCoordsList:
#         ptnumber = row[0]
#         label = row[1]
#         mapdict1[ptnumber] = label # get mapdict, such as: 2: RW
#         mapdict2[label] = ptnumber # get mapdict, such as: RW:2
#
# num = 0
# ptcoordlist = list()
# # process coordinate data and get coordinate files
# coordinate = list()
# ptlist = list()
# with open(coorDir, 'r') as roiFile:
#     coorList = csv.DictReader(roiFile, dialect='excel')
#     for row in coorList:
#         num+=1
#         coordinate.append(row['Coordinate']) # 161_126_17
#         ptlist.append(row['pt_biopsy']) # 2_111622
#
# xytuple =  dict()
# rowindex = 0
# for row in coordinate:
#     if fnmatch.fnmatch(row,'*_*'):
#         splitrow = row.split('_')
#         xytuple[rowindex] = list()
#         xytuple[rowindex].append(int(splitrow[0]))
#         xytuple[rowindex].append(int(splitrow[1]))
#         xytuple[rowindex].append(int(splitrow[2]))
#
#     else:
#         splitrow = row.split(' ')
#         xytuple[rowindex] = list()
#         xytuple[rowindex].append(int(splitrow[0]))
#         xytuple[rowindex].append(int(splitrow[1]))
#         xytuple[rowindex].append(int(splitrow[2]))
#     rowindex+=1
#
#
# # construct mapping from ptname and coordinate data
# ptidlist = list()
# ptnamelist = list()
# for row in ptlist:
#     splitrow = row.split('_')
#     ptid = splitrow[0]
#     ptidlist.append(ptid) # get ptid in list
#
# ptindex = 0
# for pt in ptidlist:
#     if pt in mapdict1:
#         ptname = mapdict1[pt]
#         if ptname not in ptnamelist:
#             ptnamelist.append(ptname)
#         ptcoordlist.append(dict())
#         ptcoordlist[ptindex][ptname] = xytuple[ptindex]
#     else:
#         if pt not in ptnamelist:
#             ptnamelist.append(pt)
#         ptcoordlist.append(dict())
#         ptcoordlist[ptindex][pt] = xytuple[ptindex]
#     ptindex+=1
#
# #print xytuple
# #print ptidlist
# #print mapdict1
# print 'ptname:',ptnamelist
# print ptcoordlist
#
#
# #print len(ptcoordlist)
#
# # remodify ptcoordlist
# newptiddict = dict()
# for ptname in ptnamelist:
#     newptiddict[ptname] = dict()
#     for tuple in ptcoordlist:
#         xylist = list()
#         for tuplename in tuple:
#             if ptname == tuplename:
#                 slicenum = tuple[tuplename][2]
#                 xnum = tuple[tuplename][0]
#                 ynum = tuple[tuplename][1]
#                 xylist.append(xnum)
#                 xylist.append(ynum)
#                 num+=1
#                 print slicenum,xnum,ynum,xylist
#
#                 if slicenum not in newptiddict[ptname]:
#                     newptiddict[ptname][slicenum] = list()
#
#                 newptiddict[ptname][slicenum].append(xylist)

#print newptiddict






