import os
import csv
import fnmatch
import numpy
import SimpleITK
import matplotlib.pyplot as plt

from mahotas.features.texture import haralick_labels
import GLCMFeatures
import LBPFeatures
import ExtendLBPFeatures
import ExtendGaborFeatures

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/RWh_slices_only/slice17'


def MitchelGrayScaleNormalization(imgArray,imgMax,imgMin):
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


dicomfile = 'Ax_T2_FSE_INTER_IM-0001-0017.dcm'
#dicomfile = 'EPI+C_IM-0003-0017.dcm'
dicomfilepath = os.path.join(rootDir,dicomfile)

xcoord = 161
ycoord = 126


LBPRadius = 1
LBPnPoints = 8 * LBPRadius
LBPMethod = 'uniform'

dicomImage = Read2DImage(dicomfilepath)

# original 8*8 box
subImage = dicomImage[ycoord-4:ycoord+4,xcoord-4:xcoord+4]

# normalized 8*8 ROI box by Dr. Mitchell
subImageMitchel = MitchelGrayScaleNormalization(subImage,subImage.max(),subImage.min())

# LBP of Dr. Mitchell
LBPRoss = LBPFeatures.calcFeatures(subImageMitchel,LBPnPoints, LBPRadius, LBPMethod)


print dicomfile

print subImage

# extended 10 * 10 box
subImageLBP = dicomImage[ycoord - 4 - LBPRadius:ycoord + 4 + LBPRadius, xcoord - 4 - LBPRadius: xcoord + 4 + LBPRadius]

# normalized 10*10 ROI box by us
extendsubImageLBP = GrayScaleNormalization(subImageLBP, subImage.max(),subImage.min())

# LBP of us
LBPs = ExtendLBPFeatures.calcFeatures(extendsubImageLBP, LBPnPoints, LBPRadius, LBPMethod)



print subImageLBP
plt.figure()

#
plt.imshow(subImageLBP, cmap='gray')
plt.title('extended 14*14 ROI')
#
# # plt.grid(True)
plt.show()








