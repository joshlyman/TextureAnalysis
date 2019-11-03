import csv
import os
import fnmatch


originalfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addPI/GBM_SlidingWindow_TextureMap_addPI'
outputfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addPI/GBM_SlidingWindow_TextureMap_addPI_Necrosis'

#PIfilepath = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/Andrea PI Prediction 0322'

Necrofilepath ='/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Prediction/GBMNecurfiles/NecrosisValue'

for texturefile in os.listdir(originalfile):
    if not fnmatch.fnmatch(texturefile,'*.csv'):
        continue

    print texturefile

    texturefilepath = os.path.join(originalfile,texturefile)

    pt = texturefile.split('_')[0]
    slicenum = texturefile.split('_')[1].split('slice')[1]
    Necrofilename = pt + ' slice' + str(slicenum) + 'Necur.csv'


    findNecropath = os.path.join(Necrofilepath, Necrofilename)

    findNdict = dict()

    with open(findNecropath, 'r') as readpifile:
        roiList = csv.DictReader(readpifile, dialect='excel')
        for aROI in roiList:

            xcoord = int(aROI['X'])
            ycoord = int(aROI['Y'])
            T1value = int(aROI['T1'])
            T1woNvalue = int(aROI['T1woN'])

            if T1value == 1 and T1woNvalue == 0:
                NecroValue = 1
            else:
                NecroValue = 0

            findNdict[str(xcoord) +'_'+ str(ycoord)] = NecroValue


    outfile= pt+'_slice'+slicenum+'_T2_ROI_Texture_Map.csv'
    outputfiledir = os.path.join(outputfile,outfile)

    with open(texturefilepath, 'r') as csvinput:
        with open(outputfiledir, 'wb') as csvoutput:
            csvwriter = csv.writer(csvoutput, dialect='excel')

            for row in csv.reader(csvinput):
                if row[0] == 'Image Contrast':
                    row.insert(7,'Necrosis(1)or not(0)')
                    csvwriter.writerow(row)

                else:
                    slicex = int(row[2])
                    slicey = int(row[3])

                    Nvalue = findNdict[str(slicex)+'_'+str(slicey)]
                    row.insert(7,str(Nvalue))
                    csvwriter.writerow(row)



