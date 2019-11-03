# In GUI version, it adds distance as input

from mahotas.features import haralick
from mahotas.features.texture import haralick_labels

angleList = ['0', '45', '90', '135']

def calcFeatures(img):
    # Remove the 14th (last) feature name since it is not calculated by default
    featureLabels = haralick_labels[:-1]
    # Return only mean value of each features for all 4 directions

    # change GLCM distance here
    rawFeatures = haralick(img,distance=1) # To do: Change here

    featureDict = {}
    for i, angle in enumerate(angleList):
        featureDict[angle] = {}
        
        for j, featureName in enumerate(featureLabels):
            featureDict[angle][featureName] = rawFeatures[i][j]

    featureDict['Avg'] = {}
    featureMean = rawFeatures.mean(axis = 0)
    for j, featureName in enumerate(featureLabels):
        featureDict['Avg'][featureName] = featureMean[j]

    return featureDict