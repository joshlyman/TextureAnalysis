import os
import csv
import fnmatch


filename = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/malignant'

def gendir(filename):
    casenum = 0

    for casefile in os.listdir(filename):
        if casefile.startswith('.'):
            continue
        if casefile.startswith('..'):
            continue
        if fnmatch.fnmatch(casefile, '*Icon*'):
            continue

        casenum+=1

        roiCCFn = list()
        roiMLOFn = list()
        contourCCFn = list()
        contourMLOFn = list()
        roiCoords = dict()
        roiDicomfile = dict()

        filename2 = os.path.join(filename, casefile)
        for lesionfile in os.listdir(filename2):
            if lesionfile.startswith('.'):
                continue
            if lesionfile.startswith('..'):
                continue
            if fnmatch.fnmatch(lesionfile, '*Icon*'):
                continue
            if fnmatch.fnmatch(lesionfile, '*texture*'):
                continue
            if fnmatch.fnmatch(lesionfile,'*CC*csv'):
                if fnmatch.fnmatch(lesionfile, '*CC*largest_rec*csv'):
                    roiCCFn.append(lesionfile)
                else:
                    contourCCFn.append(lesionfile)

            if fnmatch.fnmatch(lesionfile,'*MLO*csv'):
                if fnmatch.fnmatch(lesionfile,'*MLO*largest_rec*csv'):
                    roiMLOFn.append(lesionfile)
                else:
                    contourMLOFn.append(lesionfile)

            if fnmatch.fnmatch(lesionfile,'*DES*CC*coor.txt'):
                roiCoords['DES-CC'] = lesionfile

            if fnmatch.fnmatch(lesionfile, '*DES*CC*dcm'):
                roiDicomfile['DES-CC'] = lesionfile

            if fnmatch.fnmatch(lesionfile,'*LE*CC*coor.txt'):
                roiCoords['LE-CC'] = lesionfile

            if fnmatch.fnmatch(lesionfile,'*LE*CC*dcm'):
                roiDicomfile['LE-CC'] = lesionfile

            if fnmatch.fnmatch(lesionfile,'*DES*MLO*coor.txt'):
                roiCoords['DES-MLO'] = lesionfile

            if fnmatch.fnmatch(lesionfile,'*DES*MLO*dcm'):
                roiDicomfile['DES-MLO'] = lesionfile

            if fnmatch.fnmatch(lesionfile,'*LE*MLO*coor.txt'):
                roiCoords['LE-MLO'] = lesionfile

            if fnmatch.fnmatch(lesionfile,'*LE*MLO*dcm'):
                roiDicomfile['LE-MLO'] = lesionfile


        # print casefile
        # print roiCCFn
        # print contourCCFn
        # print roiMLOFn
        # print contourMLOFn
        # print roiCoords
        # print roiDicomfile

        return casefile,roiCoords,roiDicomfile,roiCCFn,roiMLOFn,contourCCFn,contourMLOFn


    #print casenum

gendir(filename)








