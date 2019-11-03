import csv
import os


originalfile = '/Users/yanzhexu/Desktop/Research/GBM/Final_results/GBM_features_8*8_18_LBP1.csv'
PIfilepath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Andrea PI Prediction 0311'

outputfilepath = '/Users/yanzhexu/Desktop/Research/GBM/Final_results/'

pivaluelist = list()
with open(originalfile,'r') as readcsvfile:
    readcsvfile.readline()

    for row in csv.reader(readcsvfile):
        pt = row[0]
        slicenum = int(row[2])
        slicex = int(row[3])
        slicey = int(row[4])

        PIfilename = pt+' slice'+str(slicenum) + '.csv'
        findpipath = os.path.join(PIfilepath,PIfilename)


        with open(findpipath,'r') as readpifile:
            roiList = csv.DictReader(readpifile, dialect='excel')
            for aROI in roiList:
                xcoord = int(aROI['X'])
                ycoord = int(aROI['Y'])
                if xcoord == slicex and ycoord == slicey:
                    pivalue = float(aROI['PI'])
                    pivaluelist.append(pivalue)

outfile= 'GBM_features_8*8_18_LBP1_addPI.csv'
outputfiledir = os.path.join(outputfilepath,outfile)

with open(originalfile, 'r') as csvinput:
    with open(outputfiledir, 'wb') as csvoutput:
        csvwriter = csv.writer(csvoutput, dialect='excel')

        i = 0
        for row in csv.reader(csvinput):
            if row[0] == 'Patient':
                csvwriter.writerow(row + ['PI'])
            else:
                pvalue = pivaluelist[i]
                csvwriter.writerow(row + [str(pvalue)])
                i+=1





