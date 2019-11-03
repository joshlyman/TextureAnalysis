import os
import fnmatch

rootDir = '/Users/yanzhexu/Dropbox/Prediction'
imgpath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/Hu Data Tumor Masks_V3/'
dcmDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/'

#num = 0

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


# get and store predictionfile in dict
predictiondict = dict()
for predictionfile in os.listdir(rootDir):

    if predictionfile.startswith('.'):
        continue
    if predictionfile.startswith('..'):
        continue
    if fnmatch.fnmatch(predictionfile,'*Icon*'):
        continue

    # print predictionfile

    ptsname = predictionfile.split('_')[0]
    slicename = predictionfile.split('_')[1]
    slicenum = slicename.replace('slice','')

    predictiondict[ptsname+'_'+slicenum] = predictionfile







