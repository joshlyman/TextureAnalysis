# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 21:33:23 2015

@author: rmitch
"""

from __future__ import print_function

import numpy as np
import mahotas
import mahotas.features


# perform any required intialization, and add any algorithm specific fields
# to the output header
def initAlgorithm( hdr ):
    
    hdr[ "GLCM Entropy" ] = "log2"
    
    return



def _getGLCMTestImage():
    testImage = np.array( [[0,0,1,1], [0,0,1,1], [0,2,2,2], [2,2,3,3]] )
    return testImage
    


def _getGLCMFeatureNames():
    '''
    Return a list of feature names computed from the GLCM
    
    13 features are defined. Note:
    - Uniformity is also called Angular 2nd Moment (ASM, used here) , and Energy ** 2
    - Inverse Difference Moment is also called Homogeneity (used here)

    '''
    featureNames = [ 'GLCM ASM', 'GLCM Contrast', 'GLCM Correlation', 'GLCM Sum of Squares', 'GLCM Homogeneity', \
                     'GLCM Sum Avg', 'GLCM Sum Var', 'GLCM Sum Entropy', 'GLCM Entropy', 'GLCM Diff Var',  \
                     'GLCM Diff Entropy', 'GLCM Info Meas Corr 1', 'GLCM Info Meas Corr 2' ]
    return featureNames
    

#
# Calculate GLCM (Haralick) texture features for an image
#
def computeFeatures( image ):
    # calculate the GLCM for each of 4 directions, then calculate and return 13 texture
    # features for each direction. The 14th Haralick texture feature,
    # "Maximal Correlation Coefficient" is not calculated. 
    # The Mahotas documentation claims this feature is 'unstable' and should not be used...
    f = mahotas.features.haralick( image )
    
    # calculate the mean feature value across all 4 directions
    fMean = f.mean( 0 )
    
    # calculate the range (peak-to-peak, ptp) of feature values across all 4 directions
    fRange = f.ptp( 0 )
    
    # 13 features are returned
    # Uniformity is also called Angular 2nd Moment (ASM, used here) , and Energy ** 2
    # Inverse Difference Moment is also called Homogeneity (used here)
    featureNames = _getGLCMFeatureNames()
        
    # create an empty dictionary to hold the feature name, mean and range values             
    d = {}
    
    # fill each dictionary entry, with the name (text), followed by that feature's mean and range (a tuple of floats)
    for i, name in enumerate( featureNames ):
        d[ name + " Mean" ] = fMean[ i ]    
        d[ name + " Range" ] = fRange[ i ]    

    return d
