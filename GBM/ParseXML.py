import xml.etree.ElementTree as ET
import fnmatch
import matplotlib.pyplot as plt

#rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22/ROI for +C_3D_AXIAL_IRSPGR_Fast_IM-0005-0022.xml'

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

        # xycoord.append(xc)
        # xycoord.append(yc)
        # xycoordlist.append(xycoord)
        xcoordlist.append(xc)
        ycoordlist.append(yc)


    xcoordlist.append(xcoordlist[0])
    ycoordlist.append(ycoordlist[0])

    # print childnum
    # print xcoordlist
    # print ycoordlist

    plt.plot(xcoordlist,ycoordlist,'b')

    #plt.show()
# print xycoordlist



