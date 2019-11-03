# KRAS images quality control

import SimpleITK
import matplotlib.pyplot as plt
import os
import fnmatch



rootDir = '/Users/yanzhexu/Desktop/Research/KRAS/Feb. 2017/'
# imagedcm = '/Users/yanzhexu/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/KRAS/ColonCases/Mutant/KRAS_1222_ 20130425_Delayed/Normal_liver/image.dcm'
# coordsdir = '/Users/yanzhexu/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/KRAS/ColonCases/Mutant/KRAS_1222_ 20130425_Delayed/Normal_liver/coords.txt'

Outputimage = '/Users/yanzhexu/Desktop/Research/KRAS/KRAS_Quality_Control/99check2/'

def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray


def readtxt(txtfile):
    with open(txtfile, 'r') as txtfile:
        for line in txtfile:
            linelist = line.split(';')
            x = linelist[0]
            y = linelist[1]

            plt.plot(x, y, 'r+')

#
# dicomImage = Read2DImage(imagedcm)
#
# plt.figure()
# plt.imshow(dicomImage, cmap='gray')
# readtxt(coordsdir)
#
# plt.show()

coordfile = 'coords.txt'
dcmfile = 'image.dcm'
#
#
for ptsfolder in os.listdir(rootDir):
    if ptsfolder.startswith('.'):
        continue
    if ptsfolder.startswith('..'):
        continue
    if fnmatch.fnmatch(ptsfolder, '*xlsx*'):
        continue
    if fnmatch.fnmatch(ptsfolder, '*Icon*'):
        continue

    print ptsfolder

    patientsnum = ptsfolder.split('_')[1]

    ptsfolderpath = os.path.join(rootDir,ptsfolder)
    phaseDir = dict()

    for phasefolder in os.listdir(ptsfolderpath):
        if phasefolder.startswith('.'):
            continue
        if phasefolder.startswith('..'):
            continue
        if fnmatch.fnmatch(phasefolder, '*Icon*'):
            continue

        if fnmatch.fnmatch(phasefolder,'*Lesion*'):
            phaseDir['lesion'] = phasefolder


        if fnmatch.fnmatch(phasefolder,'*Control*'):
            phaseDir['control'] = phasefolder

    if 'lesion' not in phaseDir:
        continue

    print phaseDir

    lesionfile = os.path.join(ptsfolderpath, phaseDir['lesion'])
    lesioncoordspath = os.path.join(lesionfile, coordfile)
    lesionDicom = os.path.join(lesionfile, dcmfile)

    normalfile = os.path.join(ptsfolderpath, phaseDir['control'])
    normalcoordspath = os.path.join(normalfile, coordfile)
    normalDicom = os.path.join(normalfile, dcmfile)

    dicomImage = Read2DImage(lesionDicom)


    plt.figure()
    plt.imshow(dicomImage, cmap='gray')
    dicomoutputDir = Outputimage + 'KRAS ' + patientsnum + '.png'
    plt.title('KRAS ' + patientsnum + ' dicom image')
    plt.savefig(dicomoutputDir, bbox_inches='tight')
    plt.cla()
    plt.close()


    plt.figure()
    plt.imshow(dicomImage, cmap='gray')
    lesionoutputDir = Outputimage + 'KRAS '+ patientsnum + ' ' + 'lesion ROI.png'
    readtxt(lesioncoordspath)
    plt.title('KRAS '+ patientsnum + ' lesion ROI' )
    plt.savefig(lesionoutputDir, bbox_inches='tight')
    plt.cla()
    plt.close()


    plt.figure()
    plt.imshow(dicomImage, cmap='gray')
    normaloutputDir = Outputimage + 'KRAS '+patientsnum + ' ' + 'control ROI.png'
    readtxt(normalcoordspath)
    plt.title('KRAS '+ patientsnum + ' control ROI')
    plt.savefig(normaloutputDir, bbox_inches='tight')
    plt.cla()
    plt.close()











