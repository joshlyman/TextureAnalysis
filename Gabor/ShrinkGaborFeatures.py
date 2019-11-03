import numpy as np
from skimage.filters import gabor_kernel
from scipy import ndimage

def genKernelBank(sigma_range, freq_range, out_kernel_bank):
    for i in range(4):
        theta = i / 4. * np.pi
        kernel_bank_per_theta = []
        
        for sigma in sigma_range:
            for freq in freq_range:
                kernel = np.real(gabor_kernel(freq, theta = theta, sigma_x = sigma, sigma_y = sigma))
                kernel_bank_per_theta.append(kernel)
        
        out_kernel_bank.append(kernel_bank_per_theta)

def calcFeatures(roi, kernel_bank):
    n_kernel_per_theta = len(kernel_bank[0])

    resultMean = np.zeros((4, n_kernel_per_theta))
    resultStd  = np.zeros((4, n_kernel_per_theta))
    out_mean_vec = np.zeros(4)
    out_std_vec  = np.zeros(4)

    for theta in range(4):
        for i, kernel in enumerate(kernel_bank[theta]):
            if (roi.shape[0] < kernel.shape[0] or roi.shape[1] <kernel.shape[1]):
                resultMean[theta][i] = 0
                resultStd[theta][i]  = 0
                print('ROI (%d, %d) < Kernel (%d, %d)' % 
                      (roi.shape[0], roi.shape[1], kernel.shape[0], kernel.shape[1]) )
            else:
                filteredROI = np.zeros(roi.shape)
                ndimage.filters.convolve(roi, kernel, output = filteredROI, mode = 'constant', cval = 0.0)
                
                ext_roi_radius = ( kernel.shape[0] / 2, kernel.shape[1] / 2 )
                roi_out = filteredROI[ext_roi_radius[0]:(filteredROI.shape[0] - ext_roi_radius[0]),
                                      ext_roi_radius[1]:(filteredROI.shape[1] - ext_roi_radius[1])]

                resultMean[theta][i] = roi_out.mean()
                resultStd[theta][i]  = roi_out.std()

    out_mean_vec = np.mean(resultMean, axis = 0)
    out_std_vec  = np.mean(resultStd, axis = 0)
    return np.array([out_mean_vec, out_std_vec])