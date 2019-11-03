import os
import csv
import fnmatch
import SimpleITK
import matplotlib.pyplot as plt

# read 2D dicom image
def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


def getPatientDicomImage(DicomrootDir,phasename,patient,slicenum):


    for patientfolder in os.listdir(DicomrootDir):

        if patientfolder.startswith('.'):
            continue
        if patientfolder.startswith('..'):
            continue

        if fnmatch.fnmatch(patientfolder,'*'+patient+'*'):

            patientfolderpath = os.path.join(DicomrootDir,patientfolder)

            for slicefile in os.listdir(patientfolderpath):
                if slicefile.startswith('.'):
                    continue
                if slicefile.startswith('..'):
                    continue

                if fnmatch.fnmatch(slicefile,'*'+slicenum+'*'):

                    print slicefile

                    dcmfilepath = os.path.join(patientfolderpath, slicefile)

                    dcmfiledict = dict()
                    for dcmfile in os.listdir(dcmfilepath):

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

                    DicomImagefilpath = os.path.join(dcmfilepath,dcmfiledict[phasename])
                    return DicomImagefilpath


def getfeaturesfile(featuresrootDir,phasename,patient,slicenum):

    for featuresfile in os.listdir(featuresrootDir):

        if featuresfile.startswith('.'):
            continue
        if featuresfile.startswith('..'):
            continue

        if fnmatch.fnmatch(featuresfile, '*' + patient + '*' + 'slice'+ slicenum + '*' + phasename + '*csv*'):
            # featuresfilepath = os.path.join(featuresrootDir,featuresfile)

            return featuresfile


def genFeaturesColorMap(featuresrootDir,DicomrootDir,outputDir,feature,phasename,patient,slicenum):

    DicomImage = getPatientDicomImage(DicomrootDir,phasename,patient,slicenum)

    featuresfile =getfeaturesfile(featuresrootDir,phasename,patient,slicenum)

    featuresfilepath = os.path.join(featuresrootDir,featuresfile)

    dicomImage = Read2DImage(DicomImage)

    with open(featuresfilepath,'rb') as csvfile:

        rowFile = csv.reader(csvfile, delimiter=',')

        xlist = list()
        ylist = list()
        featurelist = list()

        featureindex = 0
        for row in rowFile:

            if row[0] == 'Phase':
                featureindex = row.index(feature)

            elif row[0] == phasename:
                xlist.append(int(row[1]))
                ylist.append(int(row[2]))
                featurelist.append(float(row[featureindex]))


    plt.figure(figsize=(18, 13))

    cm = plt.cm.get_cmap('jet')
    plt.scatter(xlist, ylist, c=featurelist, cmap=cm)

    plt.colorbar()

    plt.imshow(dicomImage, cmap='gray')

    # plt.title(patient + ' slice' + slicenum + ' T2-based '+ phasename + ' '+ feature + ' FeatureMap', fontsize=30)

    plt.savefig(outputDir + ' '+ patient + ' slice' + slicenum + ' T2-based ' + phasename + ' ' + feature + ' FeatureMap.png',bbox_inches='tight')

    plt.cla()
    plt.close()




featuresrootDir = '/Users/yanzhexu/Desktop/Research/TA GUI/GBM/'

DicomrootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'

outputDir = '/Users/yanzhexu/Desktop/Research/TA GUI/GBM/'


# parameter:
# 1. featuresrootDir: input path of the features file folder
# 2. DicomrootDir: input path the patients folder
# 3. outputDir: output path to store each sliding window textures file
# 4. feature: which feature to plot feature map
# 4. phasename: modality: 'EPI', 'P', 'Q', 'RCBV', 'SPGRC', 'T2'
# 5. patient: 'CG','EB','ET','SA','SF','SH','VBr','CE','JM','JTy','MW','NT','PC','RA','RGl','RGr','Rlv','RWh'
# 6. slicenum: which slice of patient to choose


genFeaturesColorMap(featuresrootDir,DicomrootDir,outputDir,feature ='Raw Mean',phasename='P',patient='CE',slicenum='22')

