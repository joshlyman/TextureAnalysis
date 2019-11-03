import numpy
from skimage.feature import local_binary_pattern

def calcFeatures(img, nPoints, radius, method, nBins):
	lbp = local_binary_pattern(img, nPoints, radius, method)
	rawFeatures = numpy.histogram(lbp.ravel(), bins = nBins, range = (0, nBins), normed = True)
	
	return rawFeatures[0]