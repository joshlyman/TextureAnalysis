import xml.etree.ElementTree as ET
import fnmatch
import matplotlib.pyplot as plt
import numpy as np
import math
import os
import matplotlib.patches as patches

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22/ROI for +C_3D_AXIAL_IRSPGR_Fast_IM-0005-0022.xml'


def ParseXMLDrawROI(rootDir):

    tree = ET.parse(rootDir)
    root = tree.getroot()

    childnum = 0
    xcoordlist = list()
    ycoordlist = list()
    xycoordlist = list()

    boundarycheckxycoordlist = list()

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

        boundarycheckxycoordlist.append(list())
        boundarycheckxycoordlist[len(boundarycheckxycoordlist)-1].append(checkxc)
        boundarycheckxycoordlist[len(boundarycheckxycoordlist) - 1].append(checkyc)

        return boundarycheckxycoordlist


bclist = ParseXMLDrawROI(rootDir)

if [127,86] in bclist:
    print 'True'
else:
    print 'False'
