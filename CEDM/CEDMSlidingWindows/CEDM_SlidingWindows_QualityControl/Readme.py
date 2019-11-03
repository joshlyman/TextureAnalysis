# This package is for quality control on CEDM sliding windows textures
#


# Notes: Since DES Phase has low resolutions when plotting, we mainly plot LE Phase
#
# Quality control parts are as follows:
#
# 1. "51ImagesCheck.py" and "92ImagesCheck.py" plot all images with ROI
#
# 2. "CEDMLargeBoxCheck_51.py" and "CEDMLargeBoxCheck_92.py" plot all images with ROI with largest box
#
# 3. "testLargestBox.py" is to Plot CEDM images with ROI and updated largest box after correcting the box size to avoid noise
