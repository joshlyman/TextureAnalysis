import numpy
import os
import fnmatch
import csv

# If not found, 'conda install -c https://conda.anaconda.org/simpleitk SimpleITK'
import SimpleITK
import skimage
from skimage import io, exposure

def GrayScaleNormalization(imgArray):
    imgRange = imgArray.ptp()
    if imgRange == 0:
        return imgArray
    
    imgMin = imgArray.min()
    imgArray = (imgArray - imgMin) * (256.0 / imgRange)
    
    return numpy.rint(imgArray).astype(numpy.uint8)
    
def Read2DImage(fileName):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)
    
    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]
        
    return imgArray

# Image Root Dir
# rootDir = '/Users/bigpizza/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2'
rootDir = '/Users/bigpizza/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2 - NewNeg'
# rootDir = '/Users/bigpizza/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2/1FGFR2gene_0004_ 20080416_Arterial/Lesion'

roiFn = 'coords.txt'
dicomFnMask = '*.dcm'
subROIImageFN = 'roiSubImage.png'

def genROIImage():
    for dirPath, dirNames, fileNames in os.walk(rootDir):
        for dicomFn in fnmatch.filter(fileNames, dicomFnMask):
            dicomPath = os.path.join(dirPath, dicomFn)
            roiCoordsFn = os.path.join(dirPath, roiFn)
            
            dicomImage = Read2DImage(dicomPath)
            #dicomImage = GrayScaleNormalization(dicomImage)

            maskedImage = numpy.zeros(dicomImage.shape)

            coordinates = numpy.array([[-1,-1]])
            yMin = dicomImage.shape[1]
            yMax = 0
            xMin = dicomImage.shape[0]
            xMax = 0

            with open(roiCoordsFn) as f:
    			coords = f.readlines()
    			for coord in coords:
    				elements = coord.split(';')
    				coordY = int(elements[1])
    				coordX = int(elements[0])

    				if coordY < yMin:
    					yMin = coordY
    				if coordY > yMax:
    					yMax = coordY
    				if coordX < xMin:
    					xMin = coordX
    				if coordX > xMax:
    					xMax = coordX

    				maskedImage[coordY, coordX] = dicomImage[coordY, coordX]

			print yMin, yMax, xMin, xMax

			im = exposure.rescale_intensity(maskedImage[yMin:yMax, xMin:xMax], out_range='float')
			im = skimage.img_as_uint(im)
			#io.imsave(os.path.join(dirPath, subROIImageFN), im)
			folders = os.path.split(dirPath)
			folderss = os.path.split(folders[0])
			print folderss[1], folders[1]
			io.imsave(os.path.join('/Users/bigpizza/Desktop/roiFiles-NewNeg', folderss[1] + '_' + folders[1] + '_' +  subROIImageFN), im)

genROIImage()