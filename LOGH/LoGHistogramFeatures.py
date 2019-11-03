'''
Davnall, Fergus, et al. "Assessment of tumor heterogeneity: an emerging imaging tool for clinical practice?." Insights into imaging 3.6 (2012): 573-589.

The application of filters such as Laplacian of Gaussian bandpass filters in statistical-based texture analysis of an image allows the extraction of specific structures corresponding to the width of the filters. Lower filter values (filter 0.5-1.0) will highlight structures with fine textures, and higher filter values highlight structures with medium (filter 1.5-2.0) and coarse (filter 2.5) textures in the filtered image.

Typical parameters derived from the histogram analysis include the kurtosis, skewness, and standard deviation of the pixel distribution histogram, mean gray level intensity, entropy, and uniformity. Kurtosis (or the magnitude of pixel distribution), skewness (or the skewness of the pixel distribution), and the standard deviation of the pixel distribution describe the shape of the histogram representing the peak, asymmetry, and gray-level variation within the lesion. Entropy is a measure of texture irregularity, while uniformity reflects the distribution of gray levels within the tumor.
Higher entropy, lower uniformity, higher standard deviation, higher kurtosis, and positive skewness are thought to represent increased heterogeneity and portend poorer prognosis.
'''

import numpy
import scipy
from scipy import ndimage

def calcFeatures(img, sigmaList):
	LogHFeatures = numpy.zeros((sigmaList.size, 6), dtype = numpy.float)
	for i, sigma in enumerate(sigmaList):
		LoG = numpy.zeros(img.shape, dtype = numpy.float)
		ndimage.filters.gaussian_laplace(img, sigma, output = LoG)
		
		LoGHistogram, binEdges = numpy.histogram(LoG.ravel())

		nobs, minmax, mean, variance, skewness, kurtosis = scipy.stats.describe(LoG.ravel())
		std = numpy.sqrt(variance)

		density = LoGHistogram / numpy.float(nobs)
		entropy = scipy.stats.entropy(density)
		uniformity = numpy.sum(numpy.power(density, 2))

		LogHFeatures[i] = numpy.array([mean, std, skewness, kurtosis, entropy, uniformity])

	return LogHFeatures
