# check if largest box in python is same with in matlab


import csv
import numpy
import SimpleITK
import matplotlib.pyplot as plt

#rootDir1 = '/Users/yanzhexu/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2/1FGFR2gene_0004_ 20080416_Arterial/Lesion/coords.txt'

#rootDir2 =  '/Users/yanzhexu/Dropbox/ASU/Mayo Clinic/Texture Pipeline/Images/FGFR2/1FGFR2gene_0004_ 20080416_Arterial/Lesion/image_largest_rec.csv'

rootDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/malignant/Pt40/Pt40 - DES - CC_coor.txt'
rootDir2 = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/malignant/Pt40/Pt40 - DES - CC.dcm'

def Read2DImage(fileName, rotateAngle=0):
    rawImage = SimpleITK.ReadImage(fileName)
    imgArray = SimpleITK.GetArrayFromImage(rawImage)

    # Convert 3D Image to 2D
    if len(imgArray.shape) == 3:
        imgArray = imgArray[0, :, :]

    return imgArray

dicomImage = Read2DImage(rootDir2)


x1 = 595
y1 = 1186
w = 182
h = 72
x2 = x1 + w
y2 = y1 + h

xlist =list()
ylist = list()
ylist2 = list()
zlist = list()

rownum = 0
with open(rootDir, 'r') as roiFile:

    roiCoordsList = csv.reader(roiFile, delimiter=';')

    for row in roiCoordsList:
        rownum +=1
        xlist.append(int(row[0]))
        ylist.append(int(row[1]))

        if int(row[0]) <= x2 and int(row[0]) >= x1 and int(row[1]) <= y2 and int(row[1]) >= y1:
            ylist2.append(int(row[1]))

            zlist.append(int(row[2]))

# print xlist
# print ylist
#print max(ylist2)
print zlist
print numpy.mean(zlist)
print len(zlist)
print min(xlist),max(xlist)
print min(ylist),max(ylist)
# print rownum
# print len(xlist)

plt.plot(dicomImage)

plt.plot(xlist,ylist,'b')
plt.plot([x1,x1], [y1,y2], 'r')
plt.plot([x1,x2],[y1,y1],'r')
plt.plot([x1,x2],[y2,y2],'r')
plt.plot([x2,x2],[y1,y2],'r')

plt.show()


