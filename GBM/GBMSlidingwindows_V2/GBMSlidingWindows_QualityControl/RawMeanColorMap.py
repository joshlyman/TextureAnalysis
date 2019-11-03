
import csv
import matplotlib.pyplot as plt


rawmeanbeforeNormFile = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/GBM_SlidingWindow_TextureMap/CE_slice22_T2_ROI_Texture_Map.csv'
rawmeanafterNormFile ='/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/addYlabel/GBM_SlidingWindow_TextureMap/CE_slice22_T2_ROI_Texture_Map.csv'


saveDir = '/Users/yanzhexu/Desktop/Research/Sliding box GBM/MyAlgorithm_V2/Test/'


with open(rawmeanbeforeNormFile,'r') as featuresfile:
    featuresfile.readline()

    rowFile = csv.reader(featuresfile, delimiter=',')

    xlist = list()
    ylist = list()
    rawmeanlist = list()
    for row in rowFile:

        if row[0] =='SPGRC':
            xlist.append(int(row[2]))
            ylist.append(int(row[3]))
            rawmeanlist.append(float(row[42]))


cm = plt.cm.get_cmap('jet')
plt.scatter(xlist, ylist, c=rawmeanlist, cmap=cm)
plt.colorbar()

plt.savefig(saveDir + 'Raw Mean Before Normalization.png')

plt.cla()
plt.close()
# plt.show()



