# Compare sliding window P value and average P value

import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import os
import csv
import SimpleITK
import fnmatch

comparefilepath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Comparion.csv'

imgpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/Hu Data Tumor Masks_V3/'

outputfolder = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Comparsion/'


# ptsnamelist = ['RW','JTy','CE','RGr','SF','RIv','RGl','EB','ET','SH','VBr','CG','JM','MW','NT','PC','RA','SA']

# get biopsy coordinates
# biopsycoordinatefile = GBMslidingWindowBoxMappingCoordinate.getCoordinatefiles(mapDir, coorDir)

# store mapping patients folder name in ptsdict
ptsdict = dict()
for ptsfolder in os.listdir(imgpath):
    if ptsfolder.startswith('.'):
        continue
    if ptsfolder.startswith('..'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*Icon*'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*README*'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*csv'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*xlsx'):
        continue
    if fnmatch.fnmatch(ptsfolder,'*Validation*'):
        continue

    print ptsfolder

    patientname = ptsfolder.split('_')[0]
    if fnmatch.fnmatch(patientname, "*FSL*"):
        newpatientname = patientname.replace("FSL", "")
    elif fnmatch.fnmatch(patientname, "*h*"):
        newpatientname = patientname.replace("h", "")
    else:
        newpatientname = patientname
    print newpatientname

    ptsfolderpath = os.path.join(imgpath,ptsfolder)

    for T2matfile in os.listdir(ptsfolderpath):
        if T2matfile.startswith('.'):
            continue
        if T2matfile.startswith('..'):
            continue
        if fnmatch.fnmatch(T2matfile, '*Icon*'):
            continue
        if fnmatch.fnmatch(T2matfile,'*T2mask*mat'):
            T2mat = T2matfile
            print T2mat

    T2matfilepath = ptsfolder+'/'+T2mat
    ptsdict[newpatientname] = T2matfilepath

print ptsdict

def genptlist(comparefilepath):
    with open(comparefilepath, 'r') as predictFile:
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')

        ptidlist = list()
        slicenolist = list()
        xlist = list()
        ylist = list()

        for row in rowFile:
            if row[0] =='':
                continue
            ptidlist.append(str(row[0]))
            xlist.append(row[9])
            ylist.append(row[10])
            slicenolist.append(row[8])


    return ptidlist,xlist,ylist,slicenolist


ptidlist,xlist,ylist,slicenolist = genptlist(comparefilepath)
# get plist from Hu data dict


outfile =  outputfolder + 'result.csv'
i = 0
pvaluelist = list()

rowtitle = ['patientid','slicenum','X','Y','Prediction','Window_mean_Prediction','Window_std_Prediction']
with open(outfile, 'wb') as featureCSVFile:
    featureWriter = csv.writer(featureCSVFile, dialect='excel')
    featureWriter.writerow(rowtitle)


    for pt in ptidlist:
        rowlist = list()
        # get biopsy sample coordinates
        x = xlist[i]
        y = ylist[i]
        slicenum = slicenolist[i]

        print pt
        # get biopsy folder path
        ptsfolder = ptsdict[pt]
        print ptsfolder

        # get biopsy mat file and predictions matrix
        T2matfile = os.path.join(imgpath, ptsfolder)
        T2mat = sio.loadmat(T2matfile)
        T2array = T2mat['u']

        # get biopsy P value
        pvalue = T2array[y,x,slicenum]
        pvaluelist.append(pvalue)

        print slicenum
        print x,y
        print 'prediction:',pvalue



        xstr = str(x)
        ystr = str(y)
        slicenumstr = str(slicenum)
        pstr = str(pvalue)

        rowlist.append(pt)
        rowlist.append(slicenumstr)
        rowlist.append(xstr)
        rowlist.append(ystr)
        rowlist.append(pstr)


        # start to get average sliding window pvalue and std of all pixels
        pivaluelist = list()
        for xi in range(int(x)-4,int(x)+4):
            for yi in range(int(y)-4,int(y)+4):
                pivalue = T2array[yi,xi,slicenum]
                pivaluelist.append(pivalue)

        print 'number of pixels:',len(pivaluelist)

        print'\n'

        # get mean and std of window's all pixels prediction value
        meanwindowpvalue = np.mean(pivaluelist)
        stdwindowpvalue = np.std(pivaluelist)

        rowlist.append(str(meanwindowpvalue))
        rowlist.append(str(stdwindowpvalue))

        featureWriter.writerow(rowlist)

        i+=1

#print pvaluelist






