# Find max box of ACR dataset

import csv
import fnmatch
import os

import SimpleITK
import numpy
from mahotas.features.texture import haralick_labels

from GLCM import GLCMFeatures
from Gabor import ExtendGaborFeatures
from LBP import ExtendLBPFeatures


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

rootDir = '/Users/yanzhexu/Desktop/Research/MinMax/ACR'

outputDir = '/Users/yanzhexu/Desktop/Research/MinMax'

featuresOutFn = 'ACR_features.csv'

mapboxDir = '/Users/yanzhexu/Desktop/Research/MinMax/MapBox.csv'

#timepointlist = ['time_1','time_2','time_3','time_4']
dicomfile = 'image.dcm'
largestboxfile = 'largest_rec.csv'

featureTitle = ['PatientID' ,'time_point', 'xcoord','ycoord','Width', 'Height']

with open(mapboxDir, 'wb') as featureCSVFile:
    featureWriter = csv.writer(featureCSVFile, dialect='excel')
    featureWriter.writerow(featureTitle)

    for ACRfolder in os.listdir(rootDir):
        if ACRfolder.startswith('.'):
            continue
        if ACRfolder.startswith('..'):
            continue

        patientid = ACRfolder.split('_')[0] + ACRfolder.split('_')[1]


        ACRpath = os.path.join(rootDir,ACRfolder)

        for lesionfolder in os.listdir(ACRpath):
            if lesionfolder.startswith('.'):
                continue
            if lesionfolder.startswith('..'):
                continue


            ACRlesionpath = os.path.join(ACRpath,lesionfolder)

            for timepointfolder in os.listdir(ACRlesionpath):
                if timepointfolder.startswith('.'):
                    continue
                if timepointfolder.startswith('..'):
                    continue

                timepointfolderpath = os.path.join(ACRlesionpath,timepointfolder)


                boxfilepath = os.path.join(timepointfolderpath,largestboxfile)

                with open(boxfilepath, 'r') as roiFile:
                    roiList = csv.DictReader(roiFile, dialect='excel')
                    for aROI in roiList:
                        # aROIW.append(int(aROI['W']))
                        # aROIH.append(int(aROI['H']))
                        aFeature = [patientid,timepointfolder, aROI['X'],aROI['Y'],aROI['W'], aROI['H']]
                        featureWriter.writerow(aFeature)



            # timepointpath1 = os.path.join(ACRlesionpath, timepointlist[0])
            # timepointpath2 = os.path.join(ACRlesionpath, timepointlist[1])
            # timepointpath3 = os.path.join(ACRlesionpath, timepointlist[2])
            # timepointpath4 = os.path.join(ACRlesionpath, timepointlist[3])
            #
            # lesionDicom1 = os.path.join(timepointpath1, dicomfile)
            # lesionDicom2 = os.path.join(timepointpath2, dicomfile)
            # lesionDicom3 = os.path.join(timepointpath3, dicomfile)
            # lesionDicom4 = os.path.join(timepointpath4, dicomfile)
            #
            # lesionROIRectFn1 = os.path.join(timepointpath1, largestboxfile)
            # lesionROIRectFn2 = os.path.join(timepointpath2, largestboxfile)
            # lesionROIRectFn3 = os.path.join(timepointpath3, largestboxfile)
            # lesionROIRectFn4 = os.path.join(timepointpath4, largestboxfile)
            #
            #
            #
            # with open(lesionROIRectFn1, 'r') as roiFile:
            #     roiList = csv.DictReader(roiFile, dialect='excel')
            #     for aROI in roiList:
            #         xcoord1 = int(aROI['X'])
            #         ycoord1 = int(aROI['Y'])
            #         width1 = int(aROI['W'])
            #         height1 = int(aROI['H'])
            #
            # with open(lesionROIRectFn2, 'r') as roiFile:
            #     roiList = csv.DictReader(roiFile, dialect='excel')
            #     for aROI in roiList:
            #         xcoord2 = int(aROI['X'])
            #         ycoord2 = int(aROI['Y'])
            #         width2 = int(aROI['W'])
            #         height2 = int(aROI['H'])
            #
            #
            # with open(lesionROIRectFn3, 'r') as roiFile:
            #     roiList = csv.DictReader(roiFile, dialect='excel')
            #     for aROI in roiList:
            #         xcoord3 = int(aROI['X'])
            #         ycoord3 = int(aROI['Y'])
            #         width3 = int(aROI['W'])
            #         height3 = int(aROI['H'])
            #
            #
            # with open(lesionROIRectFn4, 'r') as roiFile:
            #     roiList = csv.DictReader(roiFile, dialect='excel')
            #     for aROI in roiList:
            #         xcoord4 = int(aROI['X'])
            #         ycoord4 = int(aROI['Y'])
            #         width4 = int(aROI['W'])
            #         height4 = int(aROI['H'])




        # dicomImage1 = Read2DImage(lesionDicom1)
        # dicomImage2 = Read2DImage(lesionDicom2)
        # dicomImage3 = Read2DImage(lesionDicom3)
        # dicomImage4 = Read2DImage(lesionDicom4)















