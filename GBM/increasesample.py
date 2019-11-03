
import fnmatch
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22/ROI for +C_3D_AXIAL_IRSPGR_Fast_IM-0005-0022.xml'

outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm/Testpoints/'


def increasesamplepoly(xcoordlist,ycoordlist,poly):
    newpoly = list()
    newx = list()
    newy = list()

    n = len(poly)

    p1x, p1y = poly[0]

    for i in range(1,n + 1):
        #for sampleinterval in np.arange(0,1,0.25):

        p2x, p2y = poly[i%n]

        for ratio in range(1,3):
            pix = (ratio/4) * (p2x - p1x)+p1x
            piy = (ratio/4) * (p2y - p1y)+p1y

            newpoly.append([p1x, p1y])
            newpoly.append([pix, piy])

            newx.append(p1x)
            newx.append(pix)

            newy.append(p1y)
            newy.append(piy)

        p1x, p1y = p2x, p2y

    print poly
    print len(poly)
    print newpoly
    print len(newpoly)

    print newx
    print newy
    return newx,newy

def ParseXMLDrawROI(rootDir):

    tree = ET.parse(rootDir)
    root = tree.getroot()

    childnum = 0
    xcoordlist = list()
    ycoordlist = list()
    xycoordlist = list()

    bcchecklist = list()

    for child in root.iter('string'):
        if not fnmatch.fnmatch(child.text, '*{*}*'):
            continue
        childnum += 1

        # print child.text

        # xycoord = list()
        xcoords = str(child.text).split(',')[0]
        ycoords = str(child.text).split(',')[1]

        xc = float(xcoords.split('{')[1])
        yc = float(ycoords.split('}')[0].replace(' ', ''))

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
    xycoordlist.append(xycoordlist[0])


    plt.figure()
    # draw boundary plot of ROI
    plt.plot(xcoordlist,ycoordlist,'b')

    plt.savefig(outputDir + '1.png')
    plt.cla()
    plt.close()

    plt.figure()
    xcoord, ycoord = increasesamplepoly(xcoordlist, ycoordlist, xycoordlist)
    plt.plot(xcoord,ycoord,'r')
    plt.savefig(outputDir + '2.png')
    plt.cla()
    plt.close()


ParseXMLDrawROI(rootDir)
