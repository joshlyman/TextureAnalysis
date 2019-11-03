

import csv
import os
import fnmatch


originalfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addYlabel/GBM_SlidingWindow_TextureMap'
outputfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addPI/GBM_SlidingWindow_TextureMap_addPI'

# originalfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/AddGlobalNormedRawMeaninside'

# outputfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/AddGlobalNormedRawMeaninsideAndPI'

PIfilepath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Andrea PI Prediction 0322'



for texturefile in os.listdir(originalfile):
    if not fnmatch.fnmatch(texturefile,'*.csv'):
        continue

    print texturefile

    texturefilepath = os.path.join(originalfile,texturefile)

    pt = texturefile.split('_')[0]
    slicenum = texturefile.split('_')[1].split('slice')[1]
    PIfilename = pt + ' slice' + str(slicenum) + '.csv'
    findpipath = os.path.join(PIfilepath, PIfilename)

    findPdict = dict()

    with open(findpipath, 'r') as readpifile:
        roiList = csv.DictReader(readpifile, dialect='excel')
        for aROI in roiList:

            xcoord = int(aROI['X'])
            ycoord = int(aROI['Y'])
            pvalue = float(aROI['PI'])
            findPdict[str(xcoord) +'_'+ str(ycoord)] = pvalue


    outfile= pt+'_slice'+slicenum+'_T2_ROI_Texture_Map.csv'
    outputfiledir = os.path.join(outputfile,outfile)

    with open(texturefilepath, 'r') as csvinput:
        with open(outputfiledir, 'wb') as csvoutput:
            csvwriter = csv.writer(csvoutput, dialect='excel')

            for row in csv.reader(csvinput):
                if row[0] == 'Image Contrast':
                    row.insert(6, 'PI')
                    csvwriter.writerow(row)

                else:
                    slicex = int(row[2])
                    slicey = int(row[3])

                    pvalue = findPdict[str(slicex)+'_'+str(slicey)]
                    row.insert(6, str(pvalue))
                    csvwriter.writerow(row)



