# This package is for additional Marley Breast dataset (ACR 4 time point folders).

# Position in AMIIL Data Share: “NovemberNET”
# Main code: MinMaxACR.py

# Notes:
# 1. In AMIIL dataset, there is no largest box files. You might need to run Matlab to generate largest box first,
#    then run textures files
# 2. Normalization range is to find Min/Max gray scales from 4 time point folders of each patient
# 3. In NET0003 folder, it has 2 ROIs: left and right. So totally 2 cases for this patient. 1 ROI for other patient
#    So totally 15 cases