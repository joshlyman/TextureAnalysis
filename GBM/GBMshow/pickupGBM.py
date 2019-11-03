import os
import csv
import fnmatch
import numpy
import SimpleITK
import matplotlib.pyplot as plt

from mahotas.features.texture import haralick_labels
import GLCMFeatures
import ExtendLBPFeatures
import ExtendGaborFeatures

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/RWh_slices_only/slice17'


def MitchellGrayScaleNormalization(imgArray,imgMax,imgMin):
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


#dicomfile = 'Ax_T2_FSE_INTER_IM-0001-0017.dcm'
dicomfile = 'EPI+C_IM-0003-0017.dcm'
dicomfilepath = os.path.join(rootDir,dicomfile)

xcoord = 161
ycoord = 126


dicomImage = Read2DImage(dicomfilepath)

# original 8*8 box
subImage = dicomImage[ycoord-4:ycoord+4,xcoord-4:xcoord+4]

print dicomfile
print subImage

print subImage.max(),subImage.min()

# normalized 8*8 box by us
subImageGLCM = GrayScaleNormalization(subImage, subImage.max(),subImage.min())

print subImageGLCM

# normalized 8*8 box by Dr. Mitchell
subImageGLCMRoss = MitchellGrayScaleNormalization(subImage,subImage.max(),subImage.min())

print subImageGLCMRoss

plt.figure()

plt.subplot(131)
# original 8*8 box
plt.imshow(subImage, cmap='gray')
plt.title('original 8*8 ROI')

plt.subplot(132)
# 8*8 box by us
plt.imshow(subImageGLCM, cmap='gray')
plt.title('Our normalized ROI')

plt.subplot(133)
# 8*8 box by Dr. Mitchell
plt.imshow(subImageGLCMRoss, cmap='gray')
plt.title('Dr. Mitchell normalized ROI')

plt.show()






