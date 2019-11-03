import numpy as np
from skimage.filters import gabor_kernel
from scipy import ndimage
from scipy.stats import kurtosis
from scipy.stats import skew

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

def MinMaxSubImageGen(subImage1,subImage2,subImage3,subImage4,height,width):
    # initilize min and max image matrix

    minImage = np.zeros((height, width))
    maxImage = np.zeros((height, width))

    # find min / max gray scale in each point of 4 subimage matrix
    for yi in range(height):
        for xi in range(width):
            gl1 = subImage1[yi, xi]
            gl2 = subImage2[yi, xi]
            gl3 = subImage3[yi, xi]
            gl4 = subImage4[yi, xi]

            mingl = min(gl1, gl2, gl3, gl4)
            maxgl = max(gl1, gl2, gl3, gl4)

            # put min/max gray scale in min / max image matrix
            minImage[yi, xi] = mingl
            maxImage[yi, xi] = maxgl

    return minImage,maxImage


def calcFeatures(dicomimg1, dicomimg2, dicomimg3, dicomimg4, xcoord1, ycoord1, xcoord2,ycoord2,xcoord3,ycoord3,
                 xcoord4,ycoord4, width, height, kernel_bank,maxsubimage,minsubimage):
    # xcoord and ycoord start from leftmost coordinate

    n_kernel_per_theta = len(kernel_bank[0])

    resultMean = np.zeros((4, n_kernel_per_theta))
    resultStd = np.zeros((4, n_kernel_per_theta))

    resultKurtosis = np.zeros((4, n_kernel_per_theta))
    resultSkewness = np.zeros((4, n_kernel_per_theta))

    for theta in range(4):
        for i, kernel in enumerate(kernel_bank[theta]):

            x_ext_radius = (kernel.shape[0] + 1) / 2
            y_ext_radius = (kernel.shape[1] + 1) / 2

            subImageGabor1 = dicomimg1[ycoord1 - y_ext_radius:(ycoord1 + height) + y_ext_radius, xcoord1 - x_ext_radius:(xcoord1 + width) + x_ext_radius]
            subImageGabor2 = dicomimg2[ycoord2 - y_ext_radius:(ycoord2 + height) + y_ext_radius, xcoord2 - x_ext_radius:(xcoord2 + width) + x_ext_radius]
            subImageGabor3 = dicomimg3[ycoord3 - y_ext_radius:(ycoord3 + height) + y_ext_radius, xcoord3 - x_ext_radius:(xcoord3 + width) + x_ext_radius]
            subImageGabor4 = dicomimg4[ycoord4 - y_ext_radius:(ycoord4 + height) + y_ext_radius, xcoord4 - x_ext_radius:(xcoord4 + width) + x_ext_radius]

            Gaborheight = height + 2 * y_ext_radius
            Gaborwidth = width + 2 * x_ext_radius
            MinGaborSubImage, MaxGaborSubImage = MinMaxSubImageGen(subImageGabor1, subImageGabor2, subImageGabor3, subImageGabor4,Gaborheight, Gaborwidth)

            # print xcoord1,ycoord1
            # print height,width
            # print y_ext_radius,x_ext_radius
            # gaborsize = np.shape(MinGaborSubImage)
            # print 'gabor size:',gaborsize

            roi_in = GrayScaleNormalization(MinGaborSubImage,maxsubimage,minsubimage)

            roi_out = np.zeros(roi_in.shape)

            ndimage.filters.convolve(roi_in, kernel, output=roi_out, mode='constant', cval=0.0)

            zoom_roi_out = roi_out[y_ext_radius:y_ext_radius + height, x_ext_radius:x_ext_radius+ width]

            # zoominsize = np.shape(zoom_roi_out)
            # print 'zoom in size:',zoominsize

            resultMean[theta][i] = zoom_roi_out.mean()
            resultStd[theta][i] = zoom_roi_out.std()

            # add Kurtosis and Skewness into Gabor pipeline
            outlist = list()
            zoom_roi_out_list = zoom_roi_out.tolist()
            for smalllist in zoom_roi_out_list:
                outlist += smalllist

            resultKurtosis[theta][i] = kurtosis(outlist)
            resultSkewness[theta][i] = skew(outlist)

    out_mean_vec = np.mean(resultMean, axis=0)
    out_std_vec = np.mean(resultStd, axis=0)

    out_kurtosis_vec = np.mean(resultKurtosis, axis=0)
    out_skew_vec = np.mean(resultSkewness, axis=0)

    gaborfeatures = np.column_stack((out_mean_vec, out_std_vec, out_kurtosis_vec, out_skew_vec))

    return gaborfeatures
