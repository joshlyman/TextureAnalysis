# Scan Raw Mean and Std and add into biopsy feature file from textures sliding window files

import os
import csv
import fnmatch



# texturesPath ='/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/AddGlobalNormedRawMeaninside/'

# texturesPath ='/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addYlabel/GBM_SlidingWindow_TextureMap/'

texturesPath ='/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/AddPtbyPtT2NormedRawMeaninside/'

biopsyfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/histology_(featureSet)4lab.csv'

# newbiopsyfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/histology_(featureSet)4lab_v2.csv'

# newbiopsyfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/histology_(featureSet)4lab_withoutNorm.csv'

newbiopsyfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/histology_(featureSet)4lab_PtbyPtT2Norm.csv'


# addrowlist = ['EPI-Global Normalized Raw Mean','EPI-Global Normalized Raw Std','RCBV-Global Normalized Raw Mean',
#               'RCBV-Global Normalized Raw Std','SPGRC-Global Normalized Raw Mean','SPGRC-Global Normalized Raw Std',
#               'T2-Global Normalized Raw Mean','T2-Global Normalized Raw Std','P-Global Normalized Raw Mean',
#               'P-Global Normalized Raw Std','Q-Global Normalized Raw Mean','Q-Global Normalized Raw Std']

# addrowlist = ['EPI-without Normalized Raw Mean','EPI-without Normalized Raw Std','RCBV-without Normalized Raw Mean',
#               'RCBV-without Normalized Raw Std','SPGRC-without Normalized Raw Mean','SPGRC-without Normalized Raw Std',
#               'T2-without Normalized Raw Mean','T2-without Normalized Raw Std','P-without Normalized Raw Mean',
#               'P-without Normalized Raw Std','Q-without Normalized Raw Mean','Q-without Normalized Raw Std']

addrowlist = ['EPI-Patient by Patient T2 based Normalized Raw Mean','EPI-Patient by Patient T2 based Normalized Raw Std','RCBV-Patient by Patient T2 based Normalized Raw Mean',
              'RCBV-Patient by Patient T2 based Normalized Raw Std','SPGRC-Patient by Patient T2 based Normalized Raw Mean','SPGRC-Patient by Patient T2 based Normalized Raw Std',
              'T2-Patient by Patient T2 based Normalized Raw Mean','T2-Patient by Patient T2 based Normalized Raw Std','P-Patient by Patient T2 based Normalized Raw Mean',
              'P-Patient by Patient T2 based Normalized Raw Std','Q-Patient by Patient T2 based Normalized Raw Mean','Q-Patient by Patient T2 based Normalized Raw Std']




with open(newbiopsyfile, 'wb') as writefile:
    featureWriter = csv.writer(writefile, dialect='excel')

    with open(biopsyfile,'r') as bioreadfile:
        rowFile = csv.reader(bioreadfile, delimiter=',')

        for row in rowFile:
            if row[0] == 'Patient':
                row +=addrowlist
                featureWriter.writerow(row)
            else:
                patient = row[0]
                slicenum = row[2]
                xcoord = int(row[3])
                ycoord = int(row[4])

                texturefile = patient + '_slice'+slicenum + '_T2_ROI_Texture_Map.csv'

                print texturefile
                texturesfilepath = os.path.join(texturesPath, texturefile)


                with open(texturesfilepath,'r') as texturesfile:
                    rowFile2 = csv.reader(texturesfile, delimiter=',')

                    EPIGlobalRawMean = ''
                    EPIGlobalRawStd = ''
                    RCBVGlobalRawMean = ''
                    RCBVGlobalRawStd = ''
                    SPGRCGlobalRawMean = ''
                    SPGRCGlobalRawStd = ''
                    T2GlobalRawMean = ''
                    T2GlobalRawStd = ''
                    PGlobalRawMean = ''
                    PGlobalRawStd = ''
                    QGlobalRawMean = ''
                    QGlobalRawStd = ''

                    for row2 in rowFile2:
                        if row2[0] == 'Image Contrast':
                            continue
                        else:
                            contrast = row2[0]
                            txcoord = int(row2[2])
                            tycoord = int(row2[3])

                            if contrast == 'EPI' and xcoord == txcoord and ycoord == tycoord:
                                EPIGlobalRawMean = row2[42]
                                EPIGlobalRawStd = row2[43]

                            if contrast == 'RCBV' and xcoord == txcoord and ycoord == tycoord:
                                RCBVGlobalRawMean = row2[42]
                                RCBVGlobalRawStd = row2[43]

                            if contrast == 'SPGRC' and xcoord == txcoord and ycoord == tycoord:
                                SPGRCGlobalRawMean = row2[42]
                                SPGRCGlobalRawStd = row2[43]

                            if contrast == 'T2' and xcoord == txcoord and ycoord == tycoord:
                                T2GlobalRawMean = row2[42]
                                T2GlobalRawStd = row2[43]

                            if contrast == 'P' and xcoord == txcoord and ycoord == tycoord:
                                PGlobalRawMean = row2[42]
                                PGlobalRawStd = row2[43]

                            if contrast == 'Q' and xcoord == txcoord and ycoord == tycoord:
                                QGlobalRawMean = row2[42]
                                QGlobalRawStd = row2[43]

                    addRawlist = [EPIGlobalRawMean,EPIGlobalRawStd,RCBVGlobalRawMean,RCBVGlobalRawStd,SPGRCGlobalRawMean,
                              SPGRCGlobalRawStd,T2GlobalRawMean,T2GlobalRawStd,PGlobalRawMean,PGlobalRawStd,
                              QGlobalRawMean,QGlobalRawStd]

                row += addRawlist
                featureWriter.writerow(row)



