import numpy

from GLCM import GLCMFeatures
from Gabor import GaborFeatures
from LBP import LBPFeatures
from LOGH import LoGHistogramFeatures

regularImage   = numpy.array([[1,2,3,4], [2,2,3,4], [3,2,3,4], [4,2,3,4]])
irregularImage = numpy.array([[1,2,3,4], [2,2,3,4], [3,2,3], [4,2,3]])
zeroImage      = numpy.array([[1,2,3,4], [2,2,3,4], [3,2,3,0], [4,2,3,0]])
nanImage       = numpy.array([[1,2,3,4], [2,2,3,4], [3,2,3,numpy.nan], [4,2,3,numpy.nan]])

def textureFeatures(subImage):
    glcmFeatures = GLCMFeatures.calcFeatures(subImage)
    print(glcmFeatures)

    lbpFeatures = LBPFeatures.calcFeatures(subImage, 8, 2, 'ror', 12)
    print(lbpFeatures)

    LoGHFeatures = LoGHistogramFeatures.calcFeatures(subImage, numpy.array([4.0]))
    print(LoGHFeatures)

    gaborFeatures = GaborFeatures.calcFeatures(subImage, 2.0, 0.6)
    print(gaborFeatures)

textureFeatures(nanImage)
