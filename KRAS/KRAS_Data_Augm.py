import csv
import fnmatch
import os

import SimpleITK
import numpy
import matplotlib.pyplot as plt

from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

from PIL import Image

rootDir ='/Users/yanzhexu/Desktop/Research/KRAS/Feb. 2017/krasg_1342_ 20131024_SAFIRE_Portal/Lesion/'

savDir = '/Users/yanzhexu/Desktop/Research/KRAS/Data Augmentation/'

txtDir = rootDir + 'coords.txt'

imgDir = rootDir + 'image.dcm'

csvDir = rootDir + 'largest_rec.csv'


def GetCorner(txtName):
    xs=[]
    ys=[]
    text_file = open(txtName)
    line = text_file.readline()
    while line:
        ts=line.split(";")
        xs.append(int(ts[0]))
        ys.append(int(ts[1]))
        line = text_file.readline()

    maxx = max(xs)
    maxy = max(ys)
    minx = min(xs)
    miny = min(ys)

    dx=maxx-minx
    dy=maxy-miny

    if miny-dy*0.1<0:
        miny=0
    else:
        miny-=dy*0.1

    if minx-dx*0.1<0:
        minx=0
    else:
        minx-=dx*0.1

    if maxx + dx*0.1>2560:
        maxx = 2559
    else:
        maxx += dx*0.1

    if maxy + dy * 0.1 > 3328:
        maxy = 3327
    else:
        maxy += dy * 0.1

    return int(minx),int(maxx),int(miny),int(maxy)

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



# plt.imshow(subImage,cmap="gray")
# plt.show()

def dataAugmen(subImage,samplesize,savDir):

    im = Image.fromarray(subImage)
    subImage = subImage.reshape((1,) + subImage.shape)

    subImage2 = subImage.reshape(subImage.shape + (1,))

    datagen = ImageDataGenerator(
            rotation_range=0.2,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='reflect'
    )


    i = 0
    for batch in datagen.flow(subImage2,
                              batch_size=1,
                              save_to_dir=savDir,
                              save_prefix='KRAS1',
                              save_format='jpg'):

        i += 1
        if i == samplesize:
            break  # otherwise the generator would loop indefinitely




dicomImage = Read2DImage(imgDir)
(minx, maxx, miny, maxy) = GetCorner(txtDir)

subImage = dicomImage[miny:maxy, minx:maxx]
dataAugmen(subImage,20,savDir)





