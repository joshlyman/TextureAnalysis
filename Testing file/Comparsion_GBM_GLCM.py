#!/usr/bin/env python
#=========================================================================
#
# This is for comparing GBM GLCM features between Ross's data and us
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
import matplotlib.pyplot as plt


originalfilepath  = '/Users/yanzhexu/Desktop/Research/GBM/TestGLCM/Texture_Features.csv'
# comparefilepath = '/Users/yanzhexu/Desktop/Research/GBM/TestGLCM/GBM_features_GLCM_test_X_Y_ym4xm4_yp4xp4.csv'

comparefilepath = '/Users/yanzhexu/Desktop/Research/GBM/TestGLCM/Test/GBM_features_GLCM_test_X_Y_ym3xm3_yp5xp5_Test.csv'

featuresCSVFn = '/Users/yanzhexu/Desktop/Research/GBM/TestGLCM/Test_GLCM_Comparsion.csv'


featureTitle = ['Patient','ID','slice number','X','Y','']


originaltitle = ['GLCM-ASM','GLCM-Contrast',
                 'GLCM-Correlation','GLCM-Diff Entropy',
                 'GLCM-Diff Var','GLCM-Entropy','GLCM-Homogeneity',
                 'GLCM-Info Meas Corr 1','GLCM-Info Meas Corr 2',
                 'GLCM-Sum Avg','GLCM-Sum Entropy','GLCM-Sum Var','GLCM-Sum of Squares']

comparetitle = ['Angular Second Moment_Avg','Contrast_Avg',
                'Correlation_Avg','Difference Entropy_Avg',
                'Difference Variance_Avg','Entropy_Avg','Inverse Difference Moment_Avg',
                'Information Measure of Correlation 1_Avg','Information Measure of Correlation 2_Avg',
                'Sum Average_Avg','Sum Entropy_Avg','Sum Variance_Avg','Sum of Squares: Variance_Avg']

originalphasetitle = ['EPI+C','P','Q','rCBV','SPGR+C','T2']

comparephasetitle = ['EPI','P','Q','RCBV','SPGRC','T2']

neworiginaltitle = []
for title in originalphasetitle:
    for featuretitle in originaltitle:
        newtitle = title + '-'+ featuretitle
        neworiginaltitle.append(newtitle)

newcomparetitle = []
for title in comparephasetitle:
    for featuretitle in comparetitle:
        newtitle = title + '-'+ featuretitle
        newcomparetitle.append(newtitle)


# with open(featuresCSVFn, 'wb') as featureCSVFile:
#     featureWriter = csv.writer(featureCSVFile, dialect='excel')
#     featureWriter.writerow(featureTitle)


patientlist = []
patientid = []

comparesampledict = dict()
with open(comparefilepath,'r') as comparefeatureFile:
    titlelist = csv.DictReader(comparefeatureFile,dialect='excel')
    for comparefeatures in titlelist:
        patientlist.append(comparefeatures['Patient'])
        patientid.append(comparefeatures['ID'])
        comparesampledict[comparefeatures['ID']] = []
        for title in newcomparetitle:
            comparesampledict[comparefeatures['ID']].append(comparefeatures[title])


sampledict =dict()
num = 0
with open(originalfilepath, 'r') as featureFile:
    titleList = csv.DictReader(featureFile, dialect='excel')
    for originalfeature in titleList:
        patientdict = patientid[num]
        num +=1
        sampledict[patientdict]=[]
        for title in neworiginaltitle:
            sampledict[patientdict].append(originalfeature[title])

# numsample = 0
# for sample in sampledict:
#     numsample +=1
#
#     print sample
#     print len(sampledict[sample])
#     print sampledict[sample]
# print numsample

# numsample = 0
# for sample in comparesampledict:
#     numsample +=1
#     print sample
#     print len(comparesampledict[sample])
#     print comparesampledict[sample]
# print numsample


# print len(sampledict),sampledict[0],'\n'
# print len(sampledict[1]),sampledict[1],'\n'



num = 1
x = numpy.arange(0,78,1)
for sample in patientid[48:54]:
    plt.subplot(1,3,num)
    num +=1
    y1 = sampledict[sample]
    y2 = comparesampledict[sample]
    plt.plot(x,y1,'r.-')
    plt.plot(x,y2,'b.-')
    plt.title(sample)
    print y1
    print y2
    # plt.xlabel('feature phase')
    # plt.ylabel('feature value')
    #plt.legend('Original TA features','Comparsion TA features')

# print y1
# print y2
plt.show()



