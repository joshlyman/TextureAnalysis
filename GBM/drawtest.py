# draw unusual ROI for Dr. Hu to check (only T2)

import os
import csv
import fnmatch
import numpy
import SimpleITK
import matplotlib.pyplot as plt
import ParseXML

#rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/EBFSL_slices_only/slice18'

rootDir = '/Users/yanzhexu/Desktop/Research/fromDrHu/Ax_T2_FSE_IM-0001-0020.dcm'

# def MitchellGrayScaleNormalization(imgArray,imgMax,imgMin):
#     imgRange = imgMax - imgMin
#     imgArray = (imgArray - imgMin) * (256.0 / imgRange)
#
#     # transfer to closest int
#     imgArray = numpy.rint(imgArray).astype(numpy.uint8)
#
#     return imgArray
#
# def GrayScaleNormalization(imgArray, imgMax,imgMin):
#
#     imgRange = imgMax - imgMin
#     imgArray = (imgArray - imgMin) * (255.0 / imgRange)
#
#     # transfer to closest int
#     imgArray = numpy.rint(imgArray).astype(numpy.int16)
#
#     return imgArray

def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


# dicomfile = 'Ax_T1_MP_SPGRPRE_GAD_IM-0004-0018.dcm'
# dicomfilepath = os.path.join(rootDir,dicomfile)
#
# xmlfile = 'EB_ROI_+C_Ax_T1_MP_SPGR_IM-0005-0018.xml'
# xmlpath = os.path.join(rootDir,xmlfile)

dicomImage = Read2DImage(rootDir)


plt.figure()

# original image
plt.imshow(dicomImage, cmap='gray')
#ParseXML.ParseXMLDrawROI(xmlpath)
plt.title('VBr slice 20 T2')

# plt.show()

saveDir = '/Users/yanzhexu/Desktop/Research/fromDrHu/VBrT2.png'
plt.savefig(saveDir)

plt.cla()
plt.close()






