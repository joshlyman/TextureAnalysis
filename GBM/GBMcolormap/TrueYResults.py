import csv



TrueYDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/ColorMap/Comparion.csv'


def genptlist(comparefilepath):
    with open(comparefilepath, 'r') as predictFile:
        predictFile.readline()

        rowFile = csv.reader(predictFile, delimiter=',')


        trueylist = dict()

        for row in rowFile:
            if row[0] =='':
                continue

            # dict: ptid + slicenum + X + Y
            dictrow = str(row[0])+'_'+str(row[8])+'_' + str(row[9])+'_' + str(row[10])

            trueylist[dictrow] = float(row[11])


    return trueylist

trueylist = genptlist(TrueYDir)

print trueylist
print len(trueylist)

print trueylist['RW_17_161_126']