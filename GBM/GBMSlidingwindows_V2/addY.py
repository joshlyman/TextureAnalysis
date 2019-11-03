# add Y label in textures map files

import csv
import os

rootDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/GBM_SlidingWindow_TextureMap'
outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addYlabel/GBM_SlidingWindow_TextureMap'

num=0
for replacefile in os.listdir(rootDir):
    if replacefile.startswith('.'):
        continue
    if replacefile.startswith('..'):
        continue


    num+=1
    print replacefile

    replacefiledir = os.path.join(rootDir,replacefile)
    outputfiledir = os.path.join(outputDir,replacefile)

    with open(replacefiledir,'r') as csvinput:
        with open(outputfiledir, 'wb') as csvoutput:
            csvwriter = csv.writer(csvoutput,dialect='excel')

            for row in csv.reader(csvinput):
                if row[0] == 'Image Contrast':
                    csvwriter.writerow(row+['Ylabel'])
                else:
                    csvwriter.writerow(row)


# print num


