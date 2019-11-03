# add Y label in textures map files because it takes too long to regenerate textures again


import csv
import os

rootDir = '/Users/yanzhexu/Desktop/Research/Sliding box CEDM/CEDM_TextureMap_51'
outputDir = '/Users/yanzhexu/Desktop/Research/Sliding box CEDM/addYlabel/CEDM_TextureMap_51'

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
                if row[0] == 'PatientID':
                    row[42] ='Raw_mean'
                    row[43] = 'Raw_std'
                    csvwriter.writerow(row+['Ylabel'])
                else:
                    csvwriter.writerow(row)


# print num


