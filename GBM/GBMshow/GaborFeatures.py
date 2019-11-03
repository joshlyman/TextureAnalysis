import numpy
from skimage.filters import gabor_kernel
from scipy import ndimage

def calcFeatures(img, sigma, frequency, shrinkage = 0):
	angles = 4

	resultMean = numpy.zeros(angles)
	resultStd = numpy.zeros(angles)
	filteredImg = numpy.zeros(img.shape)

	# Generate Filter Bank
	for angle in range(angles):
		theta = angle / float(angles) * numpy.pi
		aKernel = numpy.real(gabor_kernel(frequency, theta = theta,
			sigma_x = sigma, sigma_y = sigma))

        # Image Domain
		ndimage.filters.convolve(img, aKernel, output = filteredImg, mode = 'wrap')

		if shrinkage > 0:
			imgSize = filteredImg.shape
			filteredImg = filteredImg[shrinkage:imgSize[0] - shrinkage,
									  shrinkage:imgSize[1] - shrinkage]

		resultMean[angle] = filteredImg.mean()
		resultStd[angle]  = filteredImg.std()
	
	return numpy.array([resultMean.mean(), resultStd.mean()])
