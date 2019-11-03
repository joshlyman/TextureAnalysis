import numpy
from skimage.feature import local_binary_pattern

def calcFeatures(roi, nPoints, radius, method):
    lbp = local_binary_pattern(roi, nPoints, radius, method)

    imgSize = lbp.shape
    lbp = lbp[radius:imgSize[0] - radius, radius:imgSize[1] - radius]

    rawFeatures = numpy.histogram(lbp.ravel(), bins = nPoints + 2, normed = True)

    return rawFeatures[0]