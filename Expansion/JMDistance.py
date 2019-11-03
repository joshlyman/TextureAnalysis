import numpy
import math

def BhattacharyyaD(aData, bData, axis = 0):
    aMean = aData.mean(axis)
    bMean = bData.mean(axis)
    aCovM = numpy.cov(aData, rowvar = axis)
    print aCovM
    bCovM = numpy.cov(bData, rowvar = axis)

    sumABCov = aCovM + bCovM
    diffABMean = bMean - aMean

    invAPlusBCov = numpy.linalg.inv(0.5 * sumABCov)
    dotProductLeft = numpy.dot(numpy.transpose(diffABMean), invAPlusBCov)
    dotProductAll = numpy.dot(dotProductLeft, diffABMean)

    detACov = numpy.linalg.det(aCovM)
    print detACov
    detBCov = numpy.linalg.det(bCovM)
    print detBCov
    detAPlusBCov = numpy.linalg.det(sumABCov)
    print detAPlusBCov
    itemForLog = 0.5 *  detAPlusBCov / numpy.sqrt(detACov * detBCov)
    print itemForLog
    
    return 0.125 * dotProductAll # + 0.5 * math.log(itemForLog)

def JMDistance(features, classes):
    subFeatureMatrix = {}
    classList = numpy.unique(classes)
    for aClass in classList:
        subFeatureMatrix[str(aClass)] = features[classes == aClass]
    
    distanceMatrix = {}
    for i, aClass in enumerate(classList):
        for bClass in classList[i:]:
            if aClass == bClass:
                continue
            distanceMatrix[str(aClass) + ' vs ' + str(bClass)] = 2 * (1 - math.exp(-1 * BhattacharyyaD(subFeatureMatrix[str(aClass)], subFeatureMatrix[str(bClass)])))

    return distanceMatrix