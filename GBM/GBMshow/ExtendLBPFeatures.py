import numpy
from skimage.feature import local_binary_pattern

def calcFeatures(img, nPoints, radius, method, skipZoomIn = False):
    lbp = local_binary_pattern(img, nPoints, radius, method)

    if not skipZoomIn:
        imgSize = lbp.shape
        lbp = lbp[radius:imgSize[0] - radius, radius:imgSize[1] - radius]

    # lbpsize = numpy.shape(lbp)
    # print 'lbp:',lbpsize

    rawFeatures = numpy.histogram(lbp.ravel(), bins = nPoints + 2, normed = True)

    return rawFeatures[0]