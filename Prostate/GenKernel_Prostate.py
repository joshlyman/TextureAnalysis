import csv

import numpy as np
from skimage.filters import gabor_kernel

fileout = '/Users/yanzhexu/Desktop/Research/Prostate_Out/Prostate_Kernel_check.csv'

Gaborsigma_range = [0.2]
#Gaborfreq_range = [0.8]
#Gaborfreq_range = [0.8,1,1.2,1.4,1.6,1.8,2]



def genKernelBank(sigma_range, freq, kernel_bank):
    # for i in range(4):
    #     theta = i / 4. * np.pi
    #kernel_bank_per_theta = []


    for sigma in sigma_range:
        # for freq in freq_range:
        kernel = np.real(gabor_kernel(freq, theta=0, sigma_x=sigma, sigma_y=sigma))
        kernel_bank.append(kernel)

    #out_kernel_bank.append(kernel_bank_per_theta)
    return kernel_bank


#Gaborfreq_range = [0.8,1,1.2,1.4,1.6,1.8,2]
Gaborfreq_range = [0.1,0.3,0.5]
with open(fileout, 'wb') as featureCSVFile:
    for Gaborfreq in Gaborfreq_range:
        featureWriter = csv.writer(featureCSVFile, dialect='excel')
        featureTitle = ['sigma =', '0.2','freq =',Gaborfreq]
        featureWriter.writerow(featureTitle)
        kernel_bank = []

        Gaborkernel_bank = genKernelBank(Gaborsigma_range, Gaborfreq, kernel_bank)
        print Gaborkernel_bank
        for row in Gaborkernel_bank:
            featureWriter.writerow(row)






