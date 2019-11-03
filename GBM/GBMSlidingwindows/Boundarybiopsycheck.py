# My Algorithm: draw ROI plots with boundary pts and check if inside or outside, based on this to give sliding windows with details


import xml.etree.ElementTree as ET
import fnmatch
import matplotlib.pyplot as plt
import numpy as np
import math
import os
import matplotlib.patches as patches

from GBM import GBMslidingWindowBoxMappingCoordinate

#rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22/ROI for +C_3D_AXIAL_IRSPGR_Fast_IM-0005-0022.xml'

# test if all XML data can plot ROI and check inside pts
rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'
#outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm/boundarycheck/'
outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithmPlot/Boundarybiopsycheck/'

coorDir = '/Users/yanzhexu/Desktop/Research/GBM/18/patient_biopsy_coordinates_18.csv'

mapDir = '/Users/yanzhexu/Desktop/Research/GBM/18/map between pt numbers and pt label letters.txt'


#  draw each ROI box
def drawbox(xcoord,ycoord,color):
    localx1 = xcoord - 4
    localx2 = xcoord + 4
    localy1 = ycoord - 4
    localy2 = ycoord + 4
    drawplot(localx1, localx2, localy1, localy2, color)

# check if point is inside ROI boundary or outside boundary
def point_inside_polygon(x,y,poly):

    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

# draw contour rectangle plots
def drawplot(contourx1,contourx2,contoury1,contoury2,color):
    plt.plot([contourx1, contourx1], [contoury1, contoury2], color)
    plt.plot([contourx1, contourx2], [contoury1, contoury1], color)
    plt.plot([contourx1, contourx2], [contoury2, contoury2], color)
    plt.plot([contourx2, contourx2], [contoury1, contoury2], color)


# draw whole rectangle plots (get ceil and floor)
def drawSameRangeScalePlot(contourx1,contourx2,contoury1,contoury2, interval,color):

    for yinterval in range(contoury1, contoury2, interval):
        plt.plot([contourx1, contourx2], [yinterval, yinterval], color)

    for xinterval in range(contourx1, contourx2, interval):
        plt.plot([xinterval, xinterval], [contoury1, contoury2], color)


# check if coords inside boundary or outside boundary
def chooseinoutcoord(contourx1,contourx2,contoury1,contoury2,xycoord):

    # 0: inside boundary, 1: on the boundary, 2: outside boundary
    # xyboundarypos0 = list()
    # xyboundarypos1 = list()
    # xyboundarypos2 = list()

    # for each point inside rectangle plot, check if each point inside boundary or outside boundary, inside: True, outside: False
    for testx in range(contourx1,contourx2+1):
        for testy in range(contoury1,contoury2+1):

            # check if point is inside boundary or not
            inorout = point_inside_polygon(testx, testy, xycoord)

            # if inside boundary, then mark point as red
            # if real dis between bound pts and pts is larger than specific distance, then it is inside the boundary
            #if inorout == True and realdiff > 0.2:
            if inorout == True:


                #plt.plot(testx, testy, 'r+')

                # draw each ROI box, no need to show
                drawbox(testx, testy, 'r--')

            # if outside boundary, then mark point as green
            # else:
            #     plt.plot(testx, testy, 'g+')

                # xyboundarypos2.append(list())
                # xyboundarypos2[len(xyboundarypos2) - 1].append(testx)
                # xyboundarypos2[len(xyboundarypos2) - 1].append(testy)
                #

# draw ROI from coordinates in XML file
def ParseXMLDrawROI(rootDir):

    tree = ET.parse(rootDir)
    root = tree.getroot()

    childnum = 0
    xcoordlist = list()
    ycoordlist = list()
    xycoordlist = list()

    for child in root.iter('string'):
        if not fnmatch.fnmatch(child.text,'*{*}*'):
            continue
        childnum+=1

        #print child.text

        #xycoord = list()
        xcoords = str(child.text).split(',')[0]
        ycoords = str(child.text).split(',')[1]

        xc = float(xcoords.split('{')[1])
        yc = float(ycoords.split('}')[0].replace(' ',''))

        xcoordlist.append(xc)
        ycoordlist.append(yc)

        xycoordlist.append(list())
        xycoordlist[len(xycoordlist) - 1].append(xc)
        xycoordlist[len(xycoordlist) - 1].append(yc)

    xcoordlist.append(xcoordlist[0])
    ycoordlist.append(ycoordlist[0])

    #xycoordlist.append(xycoordlist[0])

    # get x/y min/max in coords
    xmin = min(xcoordlist)
    ymin = min(ycoordlist)
    xmax = max(xcoordlist)
    ymax = max(ycoordlist)

    # draw contour rectangle plot
    #drawplot(xmin,xmax,ymin,ymax,'g')

    # fix X and Y axises range in plot
    plt.xlim(40, 240)
    plt.ylim(40, 240)

    # draw whole rectangle plot
    drawSameRangeScalePlot(40,240,40,240,8,'k')

    # ceil: get higher int
    # floor: get lower int
    xmin = int(math.floor(xmin))
    xmax = int(math.ceil(xmax))
    ymin = int(math.floor(ymin))
    ymax = int(math.ceil(ymax))

    # check if coords inside boundary or outside boundary
    chooseinoutcoord(xmin,xmax,ymin,ymax,xycoordlist)

    # draw boundary plot of ROI
    plt.plot(xcoordlist,ycoordlist,'b')


    #plt.show()

def drawbiopsy(biopsycoordinatefile,newpatientname,slicenum):

    if slicenum not in biopsycoordinatefile[newpatientname]:
        return

    biopsycoordinatelist = biopsycoordinatefile[newpatientname][slicenum]

    for slicebiopsyxylist in biopsycoordinatelist:
        biopsyx = slicebiopsyxylist[0]
        biopsyy = slicebiopsyxylist[1]

        # if biopsyy not in range(min(ycoordlist) - 4, max(ycoordlist) + 4) or biopsyx not in range(min(xcoordlist) - 4,
        #                                                                                           max(xcoordlist) + 4):
        #     drawbox(biopsyx, biopsyy, 'g')

        ax = plt.gca()
        ax.add_patch(patches.Rectangle((biopsyx - 4, biopsyy - 4), 8, 8, linewidth=1, edgecolor='g', facecolor='g'))


def checkallXML(rootDir):
    # get biopsy coordinate dict from function call
    biopsycoordinatefile = GBMslidingWindowBoxMappingCoordinate.getCoordinatefiles(mapDir, coorDir)


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

        slicepathfile = os.path.join(rootDir,texturemapfile)


        for slicefile in os.listdir(slicepathfile):
            if slicefile.startswith('.'):
                continue
            if slicefile.startswith('..'):
                continue

            print slicefile

            slicenum = slicefile.replace('slice', '')
            slicenum = int(slicenum)

            dcmxmlfilepath = os.path.join(slicepathfile,slicefile)

            for xmlfile in os.listdir(dcmxmlfilepath):
                if not fnmatch.fnmatch(xmlfile, '*.xml'):
                    continue

                if fnmatch.fnmatch(xmlfile, '*NECROSIS*'):
                    continue

                if fnmatch.fnmatch(xmlfile, '*C*SPGR*') or fnmatch.fnmatch(xmlfile, '*+C*T1*') or fnmatch.fnmatch(
                        xmlfile, '*T1*+C*'):
                    T1xmlfile = xmlfile
                    print T1xmlfile

                if fnmatch.fnmatch(xmlfile, '*T2*'):
                    T2xmlfile = xmlfile
                    print T2xmlfile


            T1xmlfilepath = os.path.join(dcmxmlfilepath,T1xmlfile)
            T2xmlfilepath = os.path.join(dcmxmlfilepath,T2xmlfile)

            # original image T1
            plt.figure()
            ParseXMLDrawROI(T1xmlfilepath)
            drawbiopsy(biopsycoordinatefile,newpatientname,slicenum)
            plt.title(newpatientname + ' ' + ' ' + slicefile + ' T1')
            plt.savefig(outputDir + newpatientname + ' ' + ' ' + slicefile + ' T1.png')
            plt.cla()
            plt.close()

            # original image T2
            plt.figure()
            ParseXMLDrawROI(T2xmlfilepath)
            drawbiopsy(biopsycoordinatefile,newpatientname, slicenum)
            plt.title(newpatientname + ' ' + ' ' + slicefile + ' T2')
            plt.savefig(outputDir + newpatientname + ' ' + ' ' + slicefile + ' T2.png')
            plt.cla()
            plt.close()


checkallXML(rootDir)
