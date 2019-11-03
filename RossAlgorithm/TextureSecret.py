#!/usr/bin/env python  
#=========================================================================
#
# Extract texture features from a region-of-interest within a dicom image
#
#
#=========================================================================

#
# Change log
#
# Please update the versionInfo variable when substantial changes are made
#
# Date           Author             Changes
#
# Dec 15 2014    Ross Mitchell      Original
#
# Dec 16 2014                       Scale the ROI sub image intensities onto 0..grayScales 
#
# Dec 17 2014                       Fix the scaling to handle both int16 and uint16 pixel types
#                                   Correct bug indexing coordinates of ROI: numpy indexes arrays as [y,x] not [x,y]
#
# Jan 12 2015                       Major re-write / re-factor. Handles multiple texture algorithms now. 
#                                   Algorithms: DOST (8x8 only); GLCM; Gabor Filter Banks; Local Binary Patterns (LBP)
#
# Jan 25 2015                       Added LoGHist features. Changed feature dictionary to contain a single value per entry instead
#                                   of a ( mean, range ) pair of values. This change eliminates many columns of 0's in the output
#

from __future__ import print_function

versionInfo = "0.2b January 25 2015"

import os
import sys
import numpy as np
import fnmatch
import matplotlib.pyplot as plt
import SimpleITK as sitk
from string import maketrans

# import texture algorithms
import TextureImportAlgosSecret as texture



def imgShow( img ):
    #plt.imshow( img, cmap=plt.cm.gray )
    plt.imshow( img )
    plt.show()


def readDicomImage( fn ):
    #
    # load a dicom image. 
    #
    sImg = sitk.ReadImage( fn )
    img = sitk.GetArrayFromImage( sImg )
    # convert 3D sitk Image to 2D
    img = img[ 0,:,: ]

    return img


def scaleIntensity( image, oMin, oMax ):
    # normalize the gray scale values in the image to range from iMin to iMax

    # range of intensities in the input image
    iRange = image.ptp()
    if iRange == 0:
        return -1

    iMin = image.min()

    oRange = oMax - oMin
    
    image -= iMin        
    fImage = image * ( float(oRange) / iRange ) + oMin

    return fImage


def convertROIToPowerOf2(coords):

    cornerA = coords[0]
    cornerB = coords[1]

    centerX = int((cornerB[0] + cornerA[0])/2.0)
    centerY = int((cornerB[1] + cornerA[1])/2.0)
   
   # new_dx and _dy must be even, since they are each a power-of-2.
   # therefore, new_dx / 2 must be a whole number. Let's cast it as an int
   # so that the corner coordinates (below) are also ints
    new_dx = (np.power(2,np.ceil(np.log2(cornerB[0] - cornerA[0]))) ).astype( int )
    new_dy = (np.power(2,np.ceil(np.log2(cornerB[1] - cornerA[1]))) ).astype( int )
    
    new_cornerA = (centerX - new_dx/2  , centerY - new_dy/2  )
    new_cornerB = (centerX + new_dx/2 , centerY + new_dy/2 )
 
    return [new_cornerA , new_cornerB]


#
# extract and return a rectangular region from an image
#
def extractRect( image, c ):
    """
    coordinate 'c' contains two array indicies, in 2D or 3D
    
    Each index is a tuple corresponding to the (z,y,x) array axes, ie
    the first value in the tuple indicates which image (slice) in the volume
    to use. The second value in the tuple indicates which row in the volume, 
    and the last value in the tuple indicates which column in the volume.
    
    """
    
    subImage = -1
    
    # 2D array with indicies: [ (y0,x0), (y1,x1) ]
    if len(c[0]) == 2:
        subImage = image[ c[0][0]:c[1][0], c[0][1]:c[1][1] ]
        
    # 3D array with indicies: [ (z0,y0,x0), (z1,y1,x1) ]
    if len(c[0]) == 3 & c[0][0] == c[1][0]:
        subImage = image[ c[0][0]:c[1][0], c[0][1]:c[1][1], c[0][2]:c[1][2] ]
        subImage = image[0,:,:]

    return subImage



def parseRectROIFile( fn ):
    '''
    Parse an input file that looks something like this:
    
        256X256
        Rectangular ROI with 1 rectangle:
        (156 79)-(162 85)
    
    to extract the coordinates of the rectangle corners
     
    We assume that the input coordinates are of the form:
     
         (x0 y0)-(x1 y1)
         
    However, the verticies will be stored internally as:
     
         [ (y0,x0), (y1+1,x1+1) ]
    
    Therefore we must flip the coordinates when storing them. We also add
    1 to each coordinate of the second point. This is because numpy array
    slicing is ~exclusive~, while end users expect ROI extraction to be
    ~inclusive~.
    
    In our example, the user expects a 7x7 ROI to be extracted. If we
    pass the coordinates they have entered in the text file to numpy
    it will extract a 6x6 ROI. This is because the following code:
    
        subArray = array[ a:b ]
        
    starts at 'a' and steps up to, but not including, 'b'. To give the user
    what they expect, we add 1 to each coordinate of the 2nd point.
    
    Thus in this example the output list will look like:
    
       [ (79,156) , (86,163) ]
    '''
    # use the string method translate() to replace the chars "(-)" anywhere
    # one of them appears in the input line, with a space.
    #
    # to do this we must first setup a char translation table
    intab = "(-)"
    outtab = "   "
    trantab = maketrans( intab,outtab )


    with open( fn, "r" ) as infile:
        
        # skip the first 2 lines in the ROI file
        for i, line in enumerate( infile ):
            if i < 2: continue
        
        # replace open and close round brackets, and dashes, with spaces 
        clean = line.translate( trantab )

        # pick the numbers out of the clean input line
        nums = clean.split()
        coords = [ ( int(nums[1]), int(nums[0]) ), ( int(nums[3])+1, int(nums[2])+1 ) ] 

    return coords



def writeHeader( outFile, hdr, d ):
    '''
    
     Create a file containing a header followed by a row of feature names
    
     input consists of an output file object, a header (dictionary), followed by a dictionary of feature names. 
     Associated with each feature name is the feature value
    
     for example, suppose your feature dictionary contains the following:     
    
       { 'Ang 2nd Moment': 1.0, 
         'Entropy': 2.0,
         'Correlation': 3.0 }
    
     Then the output would look like:
    
       Ang 2nd Moment      Entropy         Correlation
       1.0                 2.0             3.0
    
    
    '''
   
    for name in sorted( hdr ):
        outFile.write( "%s:\t" % name )
        outFile.write( "%s\n" % hdr[name] )
    outFile.write( "\n" )

    for name in sorted( d ):
        outFile.write( "%s\t" % name )
    outFile.write( "\n" )

    return


def initFeatures( fnROI, fnImg, image ):

    features = {}
    
    # now add a tuple (pair) of strings to the feature list. These
    # provide info on the patient, image and ROI that produced the features
    # use a dumb trick to make these features appear first in the sorted output
    features[ "0_ROI Filename" ] = fnROI
    features[ "1_Image Filename" ] = fnImg

    imgMean = image.mean()
    imgRange = image.ptp()
    imgStd = image.std()
        
    features[ "Raw Mean" ] = imgMean
    features[ "Raw Range" ] = imgRange
    features[ "Raw StdDev" ] = imgStd
    
    return features


   
def writeFeatures( outFile, d ):
    '''
    
     Add a row of features to the output file.
     
     Features are stored in a dictionary, d. Each dictionary entry (key)
     references single feature value of type float.
     
     The dictionary entries are sorted alphabetically by key (name)
     prior to output.
    
    '''
    
    for name in sorted( d ):
        if isinstance( d[name],basestring ):
            outFile.write( "%s\t" % d[name] )
        else:
            outFile.write( "%f\t" % d[name] )

    outFile.write( "\n" )
 


           
   
#
# main()
#    
   
t = texture.importTextureAlgos()

if len ( sys.argv ) < 3:
    print( "Usage: Texture <algorithm> <root_dir> <output_file.txt>" )
    
    # normally one would just exit here. The following 2 lines let the program run
    # from the debugger, without command line input. Change the root path to meet your 
    # degub needs
    algorithm = "All"
    fnOut = "textures.txt"
    rootDir = '/Users/rmitch/Work/Research/Leland/Batchrun1withrCBVforDOST'
    #rootDir = './test'

else:
    algo = sys.argv[1]
    rootDir = sys.argv[2]
    fnOut = sys.argv[3]

algo = []
if algorithm == "All":
    for name in t:
        algo.append( name )
else:
    algo = [ algorithm ]


# identify the target directory name, image files (dicom), and ROI files
targetDir = '[Ss]lice*'
targetImg = '*.dcm'
targetROI = '*.txt'

outFile = open( fnOut, "w" )
fileCount = 0
grayScales = 256

# create a blank dictionary to hold header info
hdr = {}

# use a dumb trick to make the title appear first in the sorted output
hdr[ "0_Title" ] = "Mayo Clinic AZ Radiology MII Texture Analysis"
hdr[ "0_Version" ] = versionInfo
hdr[ "Gray Scales" ] = grayScales

# initialize each texture algorithm and
# add info to the header that is specific to each texture algorithm
INIT = 0
FEATURES = 1
for i,name in enumerate(algo):
    t[name][INIT]( hdr )


# recursivley search starting at the root directory...
# we are looking for files that match targetROI
# once found, we then iterate over all files in that dir that match targetImg
# 
# Run the texture feature extractor on the ROI within an image file
for root, dirnames, filenames in os.walk( rootDir ):
    for fnROI in fnmatch.filter( filenames, targetROI ):
        print( "Processing ROI:    ", fnROI )
        rootFnROI = os.path.join(root, fnROI)
        rect = parseRectROIFile( rootFnROI )
        
        # force all ROIs to have power-of-2 dimensions because of the DOST
        rect = convertROIToPowerOf2( rect )

        for fnImg in fnmatch.filter( filenames, targetImg ): 
            print( "          ", fnImg )
            rootFnImg = os.path.join(root, fnImg)

            inputImage = readDicomImage( rootFnImg )
            subImage = extractRect( inputImage, rect )
            subImage = scaleIntensity( subImage, 0, grayScales )
            subImage = np.rint( subImage ).astype( np.uint8 )
            
            features = initFeatures( fnROI, fnImg, subImage )
            
            for i,name in enumerate(algo):
                features.update( t[name][FEATURES]( subImage ) )

            if( fileCount == 0 ):
                writeHeader( outFile, hdr, features )
            fileCount = fileCount + 1
            writeFeatures( outFile, features )
        outFile.flush()
            
print( "File Count: ", fileCount )
            
outFile.close()
         
    



