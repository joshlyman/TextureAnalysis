# combine textures for machine learning use: Transfer to phase - texture format 

import csv
import os
import fnmatch
import numpy
from scipy.stats import kurtosis
from scipy.stats import skew

rootDir = '/Users/yanzhexu/Desktop/Research/Sliding box CEDM/addYlabel/raw92'

outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box CEDM/combineML/combinefirst_raw92/'

CombinefileOutputDir = '/Users/yanzhexu/Desktop/Research/Sliding box CEDM/combineML/'

featurecsv = 'CEDMSlidingWindows_Textures.csv'


## Notice!!: change "if remove Nan" first

# main thought: 1. filter boundary windows(1)
# 2. filter other phase, only focus on one phase
# 3. set dict for each texture and remake new texture by adding 4 main title and get new texture
# 4. store new texture in each pt file
# 5. remove 'Nan'
# 6. combine each pt file together by get title first then use Dictreader to read each texture out



# get csv title name list
def gettitle(file):
    with open(file,'r')as csvinput:
        csvlist = csv.reader(csvinput)
        csvtitle = next(csvlist)

    return csvtitle

# get phase features list dict
def getdict(replacefiledir,phase,csvphase,phasedict):

    with open(replacefiledir, 'r') as csvinput:
        texturesList = csv.DictReader(csvinput, dialect='excel')
        for texture in texturesList:

            # remove all boundary windows
            if int(texture['Boundary (1) or not (inside: 0)']) == 1:
                continue

            # scan first to remove Nan from each pt texture file
            if str(texture['Raw_Mean']) == 'nan' or str(texture['Raw_Mean']) == 'Nan':
                continue

            # Distribute each phase: 'LE-CC'
            if str(texture['Phase Name']) == csvphase:

                # start to get feature from texture
                for eachtexture in texture:

                    # rename texture to find if it exists in phasedict : 'LE_CC_LBP 00'
                    eachfeaturename = str(phase + '_' + eachtexture)

                    # filter 8 unusable texture title
                    if eachfeaturename in phasedict:


                        feature = texture[eachtexture]

                        phasedict[eachfeaturename].append(feature)

    # return phasedict including 37 phase + features name and features list
    return phasedict

# generate raw combine features for each patient
def genRawCombinefeatures(rootDir,outputDir):

    for replacefile in os.listdir(rootDir):
        if replacefile.startswith('.'):
            continue
        if replacefile.startswith('..'):
            continue

        print replacefile

        # get patient id and patient phase (benign and malignant)
        patienttitle = replacefile.split('_')[0]
        patientphase = replacefile.split('_')[1]

        # new feature file
        featuresCSVFn = outputDir + patienttitle + '_'+ featurecsv

        replacefiledir = os.path.join(rootDir, replacefile)

        # open csv file to get feature title name
        title = gettitle(replacefiledir)
        featurestitle = title[7:-1] # filter 8 unusable title

        phasenames = ['LE_CC', 'LE_MLO','DES_CC','DES_MLO']
        csvphasenames = ['LE-CC','LE-MLO','DES-CC','DES-MLO']

        with open(featuresCSVFn, 'wb') as featureCSVFile:
            featureWriter = csv.writer(featureCSVFile, dialect='excel')

            # initilize new feature names list : 'LE_CC_LBP_00_mean'....
            newphasefeaturenames = list()
            newphasefeatures = list()

            # for each phase: start to process
            for i in range(len(phasenames)):
                phase = phasenames[i] # 'LE_CC'
                csvphase = csvphasenames[i] # 'LE-CC'

                # initilize phase dict
                phasedict = dict()
                # same with phasedict, modify the order
                featurenamelist = list()

                for eachfeature in featurestitle:
                    # use 'DES_CC_LBP 00' format to create list
                    featurename = str(phase + '_' + eachfeature)
                    featurenamelist.append(featurename)
                    # print featurename

                    phasedict[featurename] = list()

                # input file name and empty phasedict, return a phase dict including features list of each phase
                returnphasedict = getdict(replacefiledir,phase,csvphase,phasedict)

                # calculate mean, std, kurtosis and skewness over all the windows
                for eachrenamefeature in featurenamelist:
                    # print eachrenamefeature

                    featurelist = returnphasedict[eachrenamefeature]
                    # print len(featurelist)

                    featurelist = [float(i) for i in featurelist]

                    meanfeaturename = eachrenamefeature + '_mean'
                    meanfeature = numpy.mean(featurelist)

                    stdfeaturename = eachrenamefeature + '_std'
                    stdfeature = numpy.std(featurelist)

                    kurtosisfeaturename = eachrenamefeature + '_kurtosis'
                    kurtosisfeature = kurtosis(featurelist)

                    skewfeaturename = eachrenamefeature + '_skewness'
                    skewfeature = skew(featurelist)

                    newphasefeaturenames.append(meanfeaturename)
                    newphasefeaturenames.append(stdfeaturename)
                    newphasefeaturenames.append(kurtosisfeaturename)
                    newphasefeaturenames.append(skewfeaturename)

                    newphasefeatures.append(meanfeature)
                    newphasefeatures.append(stdfeature)
                    newphasefeatures.append(kurtosisfeature)
                    newphasefeatures.append(skewfeature)

                # print newphasefeaturenames
                # print len(newphasefeaturenames) # totally 592
                # print newphasefeatures
                # print len(newphasefeatures) # totally 4*37*4 = 592

            newphasefeaturenames = ['PatientID'] + ['Patient Phase'] + newphasefeaturenames
            featureWriter.writerow(newphasefeaturenames)

            newphasefeatures = [str(patienttitle)] + [patientphase]+ newphasefeatures
            featureWriter.writerow(newphasefeatures)


#genRawCombinefeatures(rootDir,outputDir)

def genCombinefile(outputDir, combinefiledir):

    #combinefile = 'CEDMSlidingWindows_Textures.csv' # for CEDM 51
    combinefile = 'CEDMSlidingWindows_Textures_raw92.csv'
    combinefiledir = combinefiledir + combinefile
    #file = outputDir + 'Pt1_CEDMSlidingWindows_Textures.csv' # for CEDM 51
    file = outputDir + 'B1 _CEDMSlidingWindows_Textures.csv'
    featurestitle = gettitle(file)

    with open(combinefiledir, 'wb') as featureCSVFile:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')

        num=0

        featureWriter.writerow(featurestitle)

        for eachptfile in os.listdir(outputDir):
            if eachptfile.startswith('.'):
                continue
            if eachptfile.startswith('..'):
                continue
            num+=1


            featureslist = list()

            eachptfileDir = os.path.join(outputDir,eachptfile)

            with open(eachptfileDir, 'r') as csvinput:
                featurereader = csv.DictReader(csvinput, dialect='excel')

                # only 1 line texture
                for texture in featurereader:
                    # get texture out of dict
                    for eachfeaturetitle in featurestitle:
                        featureslist.append(texture[eachfeaturetitle])


            print featureslist
            print len(featureslist)
            featureWriter.writerow(featureslist)

        print num


genCombinefile(outputDir,CombinefileOutputDir)
