import os
import fnmatch
import csv



inputfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addPI/GBM_SlidingWindow_TextureMap_addPI_Necrosis'

outputfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addPI/GBM_SlidingWindow_TextureMap_addPI_Necrosis(removeNan)'
# outputfile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addPI/testRemoveNan'



for texturefile in os.listdir(inputfile):
    if not fnmatch.fnmatch(texturefile,'*.csv'):
        continue

    # print texturefile

    texturefilepath = os.path.join(inputfile,texturefile)

    outputfiledir = os.path.join(outputfile, texturefile)

    with open(texturefilepath, 'r') as csvinput:
        with open(outputfiledir, 'wb') as csvoutput:
            csvwriter = csv.writer(csvoutput, dialect='excel')

            for row in csv.reader(csvinput):
                if row[43] =='nan':
                    print texturefile
                    continue

                if row[44] == 'nan':
                    print texturefile
                    continue

                if row[45] == 'nan':
                    print texturefile
                    continue

                # if row[0] == 'Image Contrast':
                #     row.insert(7, 'Necrosis(1)or not(0)')
                #     csvwriter.writerow(row)
                #
                # else:
                #     slicex = int(row[2])
                #     slicey = int(row[3])
                #
                #     Nvalue = findNdict[str(slicex) + '_' + str(slicey)]
                #     row.insert(7, str(Nvalue))
                csvwriter.writerow(row)
