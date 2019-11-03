import numpy
from skimage.feature import local_binary_pattern

def calcFeatures(img, nPoints, radius, method):
	lbp = local_binary_pattern(img, nPoints, radius, method)
	rawFeatures = numpy.histogram(lbp.ravel(), bins = nPoints +2, normed = True)
	
	return rawFeatures[0]