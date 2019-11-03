# Version for GUI

import numpy as np
from skimage.filters import gabor_kernel
from scipy import ndimage

def GrayScaleNormalization(imgArray, imgMax,imgMin):

    imgRange = imgMax - imgMin
    imgArray = (imgArray - imgMin) * (255.0 / imgRange)

    # transfer to closest int
    imgArray = np.rint(imgArray).astype(np.int16)

    return imgArray

def genKernelBank(sigma_range, freq_range, out_kernel_bank):
    for i in range(4):
        theta = i / 4. * np.pi
        kernel_bank_per_theta = []

        for sigma in sigma_range:
            for freq in freq_range:
                kernel = np.real(gabor_kernel(freq, theta=theta, sigma_x=sigma, sigma_y=sigma))
                kernel_bank_per_theta.append(kernel)

        out_kernel_bank.append(kernel_bank_per_theta)
    return out_kernel_bank

def calcFeatures(dicomimg, xcoord, ycoord, width, height, kernel_bank,imgMax,imgMin):
    # xcoord and ycoord start from leftmost coordinate

    n_kernel_per_theta = len(kernel_bank[0])

    resultMean = np.zeros((4, n_kernel_per_theta))
    resultStd = np.zeros((4, n_kernel_per_theta))

    for theta in range(4):
        for i, kernel in enumerate(kernel_bank[theta]):

            x_ext_radius = (kernel.shape[0] + 1) / 2
            y_ext_radius = (kernel.shape[1] + 1) / 2

            subimageGabor = dicomimg[ycoord - y_ext_radius:(ycoord + height) + y_ext_radius, xcoord - x_ext_radius:(xcoord + width) + x_ext_radius]

            # print xcoord,ycoord
            # print y_ext_radius,x_ext_radius
            # gaborsize = np.shape(subimageGabor)
            # print 'gabor size:',gaborsize

            roi_in = GrayScaleNormalization(subimageGabor,imgMax,imgMin)

            roi_out = np.zeros(roi_in.shape)

            ndimage.filters.convolve(roi_in, kernel, output=roi_out, mode='constant', cval=0.0)

            zoom_roi_out = roi_out[y_ext_radius:y_ext_radius + height, x_ext_radius:x_ext_radius+ width]

            # zoominsize = np.shape(zoom_roi_out)
            # print 'zoom in size:',zoominsize

            resultMean[theta][i] = zoom_roi_out.mean()
            resultStd[theta][i] = zoom_roi_out.std()

    out_mean_vec = np.mean(resultMean, axis=0)
    out_std_vec = np.mean(resultStd, axis=0)
    gaborfeatures = np.column_stack((out_mean_vec,out_std_vec))

    return gaborfeatures
