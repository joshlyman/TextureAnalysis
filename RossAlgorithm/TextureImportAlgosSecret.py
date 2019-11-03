# -*- coding: utf-8 -*-
"""
Created on Sat Jan 10 10:45:59 2015

@author: rmitch
"""

def importTextureAlgos():
# import texture algorithms

    # create a dictionary of texture algorithms
    #
    # each entry will have 3 values associated with it. In order they are:
    # 1: a pointer to a function to initialize the texture algorithm.
    #    this will be called by main() before any image files are loaded
    #    this function is passed a header dictionary that will hold any
    #    header fields particular to this algorithm (typically initialization
    #    parameters)
    # 2: a pointer to a function to compute texture features. This function
    #    is passed the image region to analyze, and will return a dictionary
    #    of features
    # 3: (not usedim) a pointer to a function to prepare the ROI. This is called 
    #    before the ROI pixels are extracted from the image. This function is used to
    #    enforce any conditions on the ROI, for example, ensuring that each
    #    dimension is a power-of-2

    texture = {}
    
    # 1) GLCM methods
    import GLCMTextureSecret as glcm
    try:
        ia = getattr(glcm, "initAlgorithm")
    except AttributeError:
        raise ValueError('GLCM lacks an initAlgorithm method')
    
    try:
        cf = getattr(glcm, "computeFeatures")
    except AttributeError:
        raise ValueError('GLCM lacks a computeFeatures method')
    texture[ "GLCM" ] = ( ia, cf )
    
    
    # # 2) Gabor filter banks methods
    # import GaborTexture as gabor
    # try:
    #     ia = getattr(gabor, "initAlgorithm")
    # except AttributeError:
    #     raise ValueError('Gabor lacks an initAlgorithm method')
    #
    # try:
    #     cf = getattr(gabor, "computeFeatures")
    # except AttributeError:
    #     raise ValueError('Gabor lacks a computeFeatures method')
    # texture[ "Gabor" ] = ( ia, cf )
    #
    #
    # # 3) DOST methods
    # import DOSTTexture as dost
    # try:
    #     ia = getattr(dost, "initAlgorithm")
    # except AttributeError:
    #     raise ValueError('DOST lacks an initAlgorithm method')
    #
    # try:
    #     cf = getattr(dost, "computeFeatures")
    # except AttributeError:
    #     raise ValueError('DOST lacks a computeFeatures method')
    # texture[ "DOST" ] = ( ia, cf )
    #
    #
    # # 4) LBP methods
    # import LBPTexture as lbp
    # try:
    #     ia = getattr(lbp, "initAlgorithm")
    # except AttributeError:
    #     raise ValueError('LBP lacks an initAlgorithm method')
    #
    # try:
    #     cf = getattr(lbp, "computeFeatures")
    # except AttributeError:
    #     raise ValueError('LBP lacks a computeFeatures method')
    # texture[ "LBP" ] = ( ia, cf )
    #
    #
    # # 5) LoGHist methods
    # import LoGHistTexture as LoGHist
    # try:
    #     ia = getattr(LoGHist, "initAlgorithm")
    # except AttributeError:
    #     raise ValueError('LoGHist lacks an initAlgorithm method')
    #
    # try:
    #     cf = getattr(LoGHist, "computeFeatures")
    # except AttributeError:
    #     raise ValueError('LoGHist lacks a computeFeatures method')
    # texture[ "LoGHist" ] = ( ia, cf )
    


    return texture

