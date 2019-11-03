import os
import csv
import fnmatch
import numpy
import SimpleITK

from mahotas.features.texture import haralick_labels
import GLCMFeatures
import ExtendLBPFeatures
import ExtendGaborFeatures

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'

coorDir = '/Users/yanzhexu/Desktop/Research/GBM/patient_biopsy_coordinates.csv'

mapDir = '/Users/yanzhexu/Desktop/Research/GBM/map between pt numbers and pt label letters.txt'

outputDir = '/Users/yanzhexu/Desktop/GBMshow'

def RossGrayScaleNormalization(imgArray,imgMax,imgMin):
    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (256.0 / imgRange)

    # transfer to closest int
    imgArray = numpy.rint(imgArray).astype(numpy.uint8)

    return imgArray

def GrayScaleNormalization(imgArray, imgMax,imgMin):

    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    # transfer to closest int
    imgArray = numpy.rint(imgArray).astype(numpy.int16)

    return imgArray

def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray

#featuresOutFn = 'GBM_features_8*8_LBP1.csv'

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

# print 'patientidlist',xydict

# print coordinate
# print num

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
print ptcoordlist
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


print folderdict
# print proslice
# print len(proslice)
print proslicelist
# print len(proslicelist)

def genTextures():
    dicomnames = ['EPI', 'P', 'Q', 'RCBV', 'SPGRC', 'T2']

    #GLCMAngleList = ['0', '45', '90', '135', 'Avg']
    GLCMAngleList = ['Avg']

    featureTitle = ['Patient', 'ID', 'slice number', 'X', 'Y']

    for GLCMAngle in GLCMAngleList:
        for dicom in dicomnames:
            for featureName in haralick_labels[:-1]:
                GLCMname = dicom + '-' + featureName + '_' + GLCMAngle
                featureTitle.append(GLCMname)

    LBPRadius = 1
    LBPnPoints = 8 * LBPRadius
    LBPMethod = 'uniform'

    LBPFeatureList = []
    for dicom in dicomnames:
        for x in xrange(0, LBPnPoints + 1):
            LBPname = dicom + '-' +'LBP_%02d' % x
            LBPFeatureList.append(LBPname)
        LBPname = dicom + '-' +'LBP_Other'
        LBPFeatureList.append(LBPname)

    featureTitle = featureTitle + LBPFeatureList

    Gaborsigma_range = (0.6,1.0)
    Gaborfreq_range = (0.1, 0.3, 0.5)
    kernel_bank = []
    GaborFeatureList = ['Gabor_Mean', 'Gabor_Std']

    for dicom in dicomnames:
        for GaborSigma in Gaborsigma_range:
            for GaborFreq in Gaborfreq_range:
                for featureName in GaborFeatureList:
                    featureTitle.append(dicom + '-'+featureName + '_' + str(GaborSigma) + '_' + str(GaborFreq))

    Gaborkernel_bank = ExtendGaborFeatures.genKernelBank(Gaborsigma_range, Gaborfreq_range, kernel_bank)


    meanstdTitle = []
    for dicom in dicomnames:
        meanname = dicom +'-'+'Raw_Mean'
        stdname = dicom + '-' + 'Raw_Std'
        meanstdTitle.append(meanname)
        meanstdTitle.append(stdname)

    featureTitle = featureTitle + meanstdTitle

    ptindex = 0
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

            # aFeature = [pt, patientid, slicenum, xcoord,ycoord]

            # meanstd = list()
            # GLCM = list()
            # LBP = list()
            # Gabor = list()

            # start GLCM for each dicom
            for GLCMAngle in GLCMAngleList:
                for eachdcm in dicomnames:

                    dicomfile = dcmfiledict[eachdcm]

                    dicomfilepath = os.path.join(slicefolderpath,dicomfile)

                    dicomImage = Read2DImage(dicomfilepath)
                    subImage = dicomImage[ycoord-4:ycoord+4,xcoord-4:xcoord+4]

                    print eachdcm
                    print subImage

                    subImageGLCM = GrayScaleNormalization(subImage, subImage.max(),subImage.min())

                    print subImageGLCM

genTextures()