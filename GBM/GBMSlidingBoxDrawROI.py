# GBM sliding windows experiments (only CEFSL slice 22 + JTyFSL slice 15)
#
#
import csv
import matplotlib.pyplot as plt
import operator
import matplotlib.patches as patches
import fnmatch
import os

from GBM import GBMslidingWindowBoxMappingCoordinate
from GBM import ParseXML

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/T1 and T2 texture Maps - grid spacing 4'

ROIcoordDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'

outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ROI_SlidingWindows_Image/'

coorDir = '/Users/yanzhexu/Desktop/Research/GBM/patient_biopsy_coordinates.csv'

mapDir = '/Users/yanzhexu/Desktop/Research/GBM/map between pt numbers and pt label letters.txt'


# draw rectangle plot (whole rectangle and each ROI box)
def drawplot(contourx1,contourx2,contoury1,contoury2,color):
    plt.plot([contourx1, contourx1], [contoury1, contoury2], color)
    plt.plot([contourx1, contourx2], [contoury1, contoury1], color)
    plt.plot([contourx1, contourx2], [contoury2, contoury2], color)
    plt.plot([contourx2, contourx2], [contoury1, contoury2], color)

# draw each ROI box
def drawbox(xcoord,ycoord,color):
    localx1 = xcoord - 4
    localx2 = xcoord + 4
    localy1 = ycoord - 4
    localy2 = ycoord + 4
    drawplot(localx1, localx2, localy1, localy2, color)

# draw whole rectangle plot
def drawwholePlot(xcoordlist,ycoordlist):
    minxcoord = min(xcoordlist)
    maxxcoord = max(xcoordlist)

    minycoord = min(ycoordlist)
    maxycoord = max(ycoordlist)

    print minxcoord, maxxcoord, minycoord, maxycoord

    contourx1 = minxcoord - 4
    contourx2 = maxxcoord + 4
    contoury1 = minycoord - 4
    contoury2 = maxycoord + 4

    drawplot(contourx1, contourx2, contoury1, contoury2, 'k')

    for yinterval in range(contoury1, contoury2, 8):
        plt.plot([contourx1, contourx2], [yinterval, yinterval], 'k')

    for xinterval in range(contourx1, contourx2, 8):
        plt.plot([xinterval, xinterval], [contoury1, contoury2], 'k')

def drawSameRangeScalePlot():
    contoury1 = 40
    contoury2 = 240
    contourx1 = 40
    contourx2 = 240

    # fix X and Y axises range in plot
    plt.xlim(contourx1,contourx2)
    plt.ylim(contoury1,contoury2)

    for yinterval in range(contoury1, contoury2, 8):
        plt.plot([contourx1, contourx2], [yinterval, yinterval], 'k')

    for xinterval in range(contourx1, contourx2, 8):
        plt.plot([xinterval, xinterval], [contoury1, contoury2], 'k')


# get biopsy coordinate dict from function call
biopsycoordinatefile = GBMslidingWindowBoxMappingCoordinate.getCoordinatefiles(mapDir,coorDir)

# main
# start to get texture map file (T1 and T2)
for texturemapfile in os.listdir(rootDir):

    if texturemapfile.startswith('.'):
        continue
    if texturemapfile.startswith('..'):
        continue

    print texturemapfile

    patientname = texturemapfile.split('_')[0]
    if fnmatch.fnmatch(patientname,"*FSL*"):
        newpatientname = patientname.replace("FSL","")
    elif fnmatch.fnmatch(patientname,"*h*"):
        newpatientname = patientname.replace("h","")
    else:
        newpatientname = patientname
    print newpatientname
    #print patientname


    slicenum = texturemapfile.split('_')[1].replace('slice','')
    slicenum = int(slicenum)
    print slicenum

    TROI = texturemapfile.split('_')[2]
    print TROI

    TROInum = TROI[0] + TROI[1]
    print TROInum

    xmlfileDir = ROIcoordDir +'/'+patientname + '_slices_only/slice'+str(slicenum)

    for xmlfile in os.listdir(xmlfileDir):
        if not fnmatch.fnmatch(xmlfile, '*.xml'):
            continue

        if fnmatch.fnmatch(xmlfile,'*NECROSIS*'):
            continue

        if fnmatch.fnmatch(xmlfile, '*C*SPGR*') or fnmatch.fnmatch(xmlfile, '*+C*T1*') or fnmatch.fnmatch(xmlfile,'*T1*+C*'):
            T1file = xmlfile
            print T1file

        if fnmatch.fnmatch(xmlfile, '*T2*'):
            T2file = xmlfile
            print T2file

    if TROInum == 'T1':
        xmlpath = os.path.join(xmlfileDir,T1file)

    if TROInum == 'T2':
        xmlpath = os.path.join(xmlfileDir, T2file)

    # start to get file and draw

    plt.figure()
    mincontourlist = list()
    maxcontourlist = list()

    xydict = dict()
    xcoordlist = list()
    ycoordlist = list()

    texturefile = os.path.join(rootDir,texturemapfile)
    with open(texturefile, 'r') as roiFile:
        for i in range(9):
            roiFile.readline()

        rowFile = csv.reader(roiFile, delimiter=',')
        for row in rowFile:

            # only study one contrast since others are same
            if row[0]!= 'EPI+C':
                continue

            # get y coordinate
            ycoord = int(float(row[2]))
            ycoordlist.append(ycoord)
            #print ycoord

            # get x coordinate
            xcoord = int(float(row[3]))
            xcoordlist.append(xcoord)
            #print xcoord

            # draw each ROI box, no need to show
            drawbox(xcoord,ycoord,'r--')

            # store ycoord tuple in dict (ycoord: (xmin to xmax)), if not exist, create one
            if not ycoord in xydict:
                xydict[ycoord]= list()

            # store ycoord tuple in each ycoord dict
            xydict[ycoord].append(xcoord)

    # sort xydict
    xydictsort = sorted(xydict.items(), key=operator.itemgetter(0))
    #print xydictsort

    # draw ROI from xml data file

    ParseXML.ParseXMLDrawROI(xmlpath)

    # contour store y,minx and y,maxx in mincontourlist and maxcontourlist
    # for index,tuple in enumerate(xydictsort):
    #
    #     mincontourlist.append(list())
    #     maxcontourlist.append(list())
    #
    #     # get ycoo from tuple
    #     ycoo = tuple[0]
    #     print ycoo
    #     minxcoo = min(xydict[ycoo])
    #     mincontourlist[index].append(ycoo)
    #     mincontourlist[index].append(minxcoo)
    #
    #     maxxcoo = max(xydict[ycoo])
    #     maxcontourlist[index].append(ycoo)
    #     maxcontourlist[index].append(maxxcoo)
    #
    # # connect points in mincontourlist (vary from y)
    # for i in range(len(mincontourlist)):
    #     if (i+1)!= len(mincontourlist):
    #         draw1 = mincontourlist[i]
    #         draw2 = mincontourlist[i+1]
    #     y1 = draw1[0]
    #     x1 = draw1[1]
    #     y2 = draw2[0]
    #     x2 = draw2[1]
    #     #print y1,x1,y2,x2
    #     plt.plot([x1, x2], [y1, y2], 'r',linewidth=5)
    #
    # # connect points in maxcontourlist (vary from y)
    # for i in range(len(maxcontourlist)):
    #     if (i+1)!= len(maxcontourlist):
    #         draw1 = maxcontourlist[i]
    #         draw2 = maxcontourlist[i+1]
    #     y1 = draw1[0]
    #     x1 = draw1[1]
    #     y2 = draw2[0]
    #     x2 = draw2[1]
    #     #print y2,x2,y1,x1
    #     plt.plot([x1, x2], [y1, y2], 'r',linewidth=5)
    #
    # # connect ymin,xmin to ymin,xmax (bottom line) and connect ymax,xmin to ymax,xmax (top line)
    # # since for ymin and ymax, interval of [xmin, xmax] is always 4, so
    # # it is okay to only connect (ymin,xmin) to (ymin,xmax) and (ymax,xmin) to (ymax,xmax)
    #
    # #print mincontourlist
    # #print maxcontourlist
    # yminxmin = mincontourlist[0]
    # ymaxxmin = mincontourlist[-1]
    # yminxmax = maxcontourlist[0]
    # ymaxxmax = maxcontourlist[-1]
    #
    # # element in list is stored as (y,x)
    # y1 = yminxmin[0]
    # x1 = yminxmin[1]
    # y2 = yminxmax[0]
    # x2 = yminxmax[1]
    # plt.plot([x1, x2], [y1, y2], 'r',linewidth=5)
    #
    # y1 = ymaxxmin[0]
    # x1 = ymaxxmin[1]
    # y2 = ymaxxmax[0]
    # x2 = ymaxxmax[1]
    # plt.plot([x1, x2], [y1, y2], 'r',linewidth=5)

    # draw whole rectangle ROI,
    # change: change to same range of X and Y and same scale of X and Y
    # drawwholePlot(xcoordlist,ycoordlist)
    drawSameRangeScalePlot()

    # get biopsy coordinates from dict
    if slicenum not in biopsycoordinatefile[newpatientname]:

        plt.xlabel("X coordinate")
        plt.ylabel("Y coordinate")

        plt.title(newpatientname + '_' + 'slice' + str(slicenum) + '_' + TROI + ' and sliding windows(biopsy samples not found)')
        plt.savefig(outputDir + newpatientname + '_' + str(slicenum) + '_' + TROI + '.png')

        # plt.annotate('Not found biopsy sample')
        print 'one case finished \n'

    else:
        biopsycoordinatelist = biopsycoordinatefile[newpatientname][slicenum]

        for slicebiopsyxylist in biopsycoordinatelist:
            biopsyx = slicebiopsyxylist[0]
            biopsyy = slicebiopsyxylist[1]

            if biopsyy not in range(min(ycoordlist)-4,max(ycoordlist)+4) or biopsyx not in range(min(xcoordlist)-4,max(xcoordlist)+4):
                drawbox(biopsyx,biopsyy,'g')

            ax = plt.gca()
            ax.add_patch(patches.Rectangle((biopsyx-4,biopsyy-4),8,8,linewidth=1,edgecolor='g',facecolor='g'))

        plt.xlabel("X coordinate")
        plt.ylabel("Y coordinate")

        # get biopsy sample coordinates from csv and put in plot
        plt.title(newpatientname + '_' + 'slice' + str(slicenum) + '_' + TROI + ' and sliding windows(biopsy samples inside)')
        plt.savefig(outputDir+newpatientname+'_'+str(slicenum)+'_'+TROI+'.png')

        print 'one case finished \n'


