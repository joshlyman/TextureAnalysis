# Experiment: test if text file coordinates can be read or not

import matplotlib.pyplot as plt


txtDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/benign/Pt1/Pt1 - LE - CC_coor.txt'


with open(txtDir,'r') as txtfile:
    for line in txtfile:
        linelist = line.split(';')
        x = linelist[0]
        y = linelist[1]

        plt.plot(x,y,'r+')

        # txtx.append(x)
        # txty.append(y)



# print len(txtx)
# print len(txty)