# My Algorithm: draw ROI plots with boundary pts and check if inside or outside, based on this to give sliding windows with details
#

import xml.etree.ElementTree as ET
import fnmatch
import matplotlib.pyplot as plt
import numpy as np
import math
import os

#rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22/ROI for +C_3D_AXIAL_IRSPGR_Fast_IM-0005-0022.xml'

# test if all XML data can plot ROI and check inside pts
rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset'
#outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm/boundarycheck/'
outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithmPlot/Boundarycheck2/'


def drawbox(xcoord,ycoord,dis,color):
    localx1 = xcoord - dis
    localx2 = xcoord + dis
    localy1 = ycoord - dis
    localy2 = ycoord + dis
    drawplot(localx1, localx2, localy1, localy2, color)

# increase sample points in boundary points of XML file
# def increasesamplepoly(poly):
#     newpoly = list()
#     bcchecklist = list()
#     n = len(poly)
#
#     p1x, p1y = poly[0]
#
#     for i in range(1,n + 1):
#         #for sampleinterval in np.arange(0,1,0.25):
#
#         p2x, p2y = poly[i % n]
#
#         checkx1c = int(np.rint(p1x))
#         checky1c = int(np.rint(p1y))
#         bcchecklist.append(list())
#         bcchecklist[len(bcchecklist) - 1].append(checkx1c)
#         bcchecklist[len(bcchecklist) - 1].append(checky1c)
#
#         # set sample ratio to get more points
#         for ratio in range(1):
#             pix = (ratio/2) * (p2x - p1x)+p1x
#             piy = (ratio/2) * (p2y - p1y)+p1y
#
#             # new poly after using increasing sample points method
#             newpoly.append([p1x, p1y])
#             newpoly.append([pix, piy])
#
#             # get close int of x/y and store in bcchecklist
#             checkxic = int(np.rint(pix))
#             checkyic = int(np.rint(piy))
#             bcchecklist.append(list())
#             bcchecklist[len(bcchecklist) - 1].append(checkxic)
#             bcchecklist[len(bcchecklist) - 1].append(checkyic)
#
#         p1x, p1y = p2x, p2y
#
#     return bcchecklist


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

    # fix X and Y axises range in plot
    plt.xlim(contourx1, contourx2)
    plt.ylim(contoury1, contoury2)

    for yinterval in range(contoury1, contoury2, interval):
        plt.plot([contourx1, contourx2], [yinterval, yinterval], color)

    for xinterval in range(contourx1, contourx2, interval):
        plt.plot([xinterval, xinterval], [contoury1, contoury2], color)


# check if coords inside boundary or outside boundary
def chooseinoutcoord(contourx1,contourx2,contoury1,contoury2,xycoord,bcchecklist):

    # 0: inside boundary, 1: on the boundary, 2: outside boundary
    # xyboundarypos0 = list()
    # xyboundarypos1 = list()
    # xyboundarypos2 = list()


    # for each point inside rectangle plot, check if each point inside boundary or outside boundary, inside: True, outside: False
    for testx in range(contourx1,contourx2+1):
        for testy in range(contoury1,contoury2+1):

            # check if point is inside boundary or not
            inorout = point_inside_polygon(testx, testy, xycoord)

            if inorout == True:
                if [testx,testy] in bcchecklist:
                    plt.plot(testx, testy, 'r+')
                    drawbox(testx,testy,4,'r')



                    # get diff between boundary pts and test (x,y) pts
            # diffbound = list()
            # for boundxy in xycoord:
            #     boundx = boundxy[0]
            #     boundy = boundxy[1]
            #     diff = abs(boundx-testx) + abs(boundy-testy)
            #     diffbound.append(diff)

            # get closest diff between boundary pts and test (x,y)
            #realdiff = min(diffbound)

            # if inside boundary, then mark point as red
            # if real dis between bound pts and pts is larger than specific distance, then it is inside the boundary
            #if inorout == True and realdiff > 0.2:


            # if inorout == True:
            #     plt.plot(testx, testy, 'r+')

                # xyboundarypos0.append(list())
                # xyboundarypos0[len(xyboundarypos0) - 1].append(testx)
                # xyboundarypos0[len(xyboundarypos0) - 1].append(testy)

            # if real dis between bound pts and pts is smaller than specific distance, then it is on the boundary
            # elif inorout == True and realdiff <0.2:
            #     plt.plot(testx, testy, 'r+')
            #
            #     x1 = testx - 4
            #     x2 = testx + 4
            #     y1 = testy - 4
            #     y2 = testy + 4
            #
            #     drawplot(x1, x2, y1, y2, 'r')
            #
            #     xyboundarypos1.append(list())
            #     xyboundarypos1[len(xyboundarypos1) - 1].append(testx)
            #     xyboundarypos1[len(xyboundarypos1) - 1].append(testy)

            # if outside boundary, then mark point as green

            # else:
            # #elif inorout == False:
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

    bcchecklist = list()

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

        checkxc = int(np.rint(xc))
        checkyc = int(np.rint(yc))

        xcoordlist.append(xc)
        ycoordlist.append(yc)

        xycoordlist.append(list())
        xycoordlist[len(xycoordlist) - 1].append(xc)
        xycoordlist[len(xycoordlist) - 1].append(yc)

        bcchecklist.append(list())
        bcchecklist[len(bcchecklist) - 1].append(checkxc)
        bcchecklist[len(bcchecklist) - 1].append(checkyc)


    xcoordlist.append(xcoordlist[0])
    ycoordlist.append(ycoordlist[0])

    #bcchecklist = increasesamplepoly(xycoordlist)

    #xycoordlist.append(xycoordlist[0])

    # get x/y min/max in coords
    xmin = min(xcoordlist)
    ymin = min(ycoordlist)
    xmax = max(xcoordlist)
    ymax = max(ycoordlist)

    # draw contour rectangle plot
    #drawplot(xmin,xmax,ymin,ymax,'k')



    # ceil: get higher int
    # floor: get lower int
    xmin = int(math.floor(xmin))
    xmax = int(math.ceil(xmax))
    ymin = int(math.floor(ymin))
    ymax = int(math.ceil(ymax))

    # draw whole rectangle plot
    drawSameRangeScalePlot(xmin,xmax,ymin,ymax,8,'k')

    # plt.xlim(40, 240)
    # plt.ylim(40, 240)
    #
    # # draw whole rectangle plot
    #drawSameRangeScalePlot(40, 240, 40, 240, 8, 'k')


    # check if coords inside boundary or outside boundary
    chooseinoutcoord(xmin,xmax,ymin,ymax,xycoordlist,bcchecklist)

    # draw boundary plot of ROI
    plt.plot(xcoordlist,ycoordlist,'b')



    #plt.show()


def checkallXML(rootDir):

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
            plt.title(newpatientname + ' ' + ' ' + slicefile + ' T1')
            plt.savefig(outputDir + newpatientname + ' ' + ' ' + slicefile + ' T1.png')
            plt.cla()
            plt.close()

            # original image T2
            plt.figure()
            ParseXMLDrawROI(T2xmlfilepath)
            plt.title(newpatientname + ' ' + ' ' + slicefile + ' T2')
            plt.savefig(outputDir + newpatientname + ' ' + ' ' + slicefile + ' T2.png')
            plt.cla()
            plt.close()


checkallXML(rootDir)
