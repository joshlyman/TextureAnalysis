import os
import csv
import SimpleITK
import numpy

inputpath = '/Users/yanzhexu/Dropbox/using ML-PI to predict density and correlate with survival/Textures Pipeline data/'

imagespath = '/Users/yanzhexu/Dropbox/using ML-PI to predict density and correlate with survival/data from Andrea/EOR_ML_PI_Shared Regridded_Data/'

outputfolder = '/Users/yanzhexu/Desktop/Research/EOR_Andrea/Update/'


def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray



for subfolder in os.listdir(inputpath):

    if subfolder.startswith('.'):
        continue
    if subfolder.startswith('..'):
        continue

    print subfolder

    # if subfolder !='AR3530':
    #     continue

    subfolderpath = os.path.join(inputpath,subfolder)

    for featurefile in os.listdir(subfolderpath):
        if featurefile.startswith('.'):
            continue
        if featurefile.startswith('..'):
            continue

        print featurefile

        slicenum = featurefile.split('_')[1].split('slice')[1]

        print slicenum

        # T1 file
        T1dcmfilename = subfolder + 'T1Gd_' + slicenum + '.dcm'

        # T2 file
        T2dcmfilename = subfolder + 'T2_' + slicenum +'.dcm'


        casefolder = os.path.join(imagespath,subfolder)
        T1casefolder = os.path.join(casefolder,'T1Gd')
        T1dcmpath = os.path.join(T1casefolder,T1dcmfilename)

        if not os.path.exists(T1dcmpath):
            T1dcmfilename = subfolder + '_T1Gd_' + slicenum + '.dcm'
            T1dcmpath = os.path.join(T1casefolder, T1dcmfilename)


        T2casefolder = os.path.join(casefolder,'T2')
        T2dcmpath = os.path.join(T2casefolder,T2dcmfilename)
        if not os.path.exists(T2dcmpath):
            T2dcmfilename = subfolder + '_T2_' + slicenum + '.dcm'
            T2dcmpath = os.path.join(T2casefolder, T2dcmfilename)

        featurefilepath = os.path.join(subfolderpath, featurefile)

        featuresOutFn = 'ROI_Texture_Map.csv'

        T2featuresOutFn = subfolder + '_slice' + slicenum + '_' + 'T2' + '_' + featuresOutFn
        outputfolderpath = os.path.join(outputfolder,subfolder)

        outputfeaturefilepath = os.path.join(outputfolderpath,T2featuresOutFn)

        with open(outputfeaturefilepath,'wb') as writefile:
            featureWriter = csv.writer(writefile, dialect='excel')

            with open(featurefilepath, 'r') as featuresfile:
                # featuresfile.readline()
                rowFile = csv.reader(featuresfile, delimiter=',')

                for row in rowFile:
                    if row[1] =='Image.Contrast':
                        featureWriter.writerow(row)
                    else:
                        T = row[1]
                        xcoord = int(row[3])
                        ycoord = int(row[4])

                        if T == 'T1':
                            dicomfile = T1dcmpath
                        else:
                            dicomfile = T2dcmpath

                        dicomImage = Read2DImage(dicomfile)

                        subImage = dicomImage[ycoord - 4:ycoord + 4, xcoord - 4:xcoord + 4]
                        #dicommean, dicomstd = Norm_Mean_Std_LargestBox(subImage, subImage.max(), subImage.min())

                        Raw_mean = numpy.mean(subImage)
                        Raw_std = numpy.std(subImage)

                        row[41] = Raw_mean
                        row[42] = Raw_std

                        featureWriter.writerow(row)

