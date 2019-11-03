# This package is for CEDM breast images.
#
# Sub packages also included inside: CEDM sliding windows textures folder
# and CEDM sliding windows quality control folder
#
#
# Position in AMIIL Data Share: “Seed-Breast Imaging Data (CEDM-Bhavika)”
# Note: This is original dataset.

# 4 Phases: DES-CC, DES-MLO, LE-CC, LE-MLO


# 1. Later we did quality control and found there is existing some noises in some images. We change the
#    box sizes and manually update them in those cases. So please find modifies box cases file and update box size in dataset
#
# 2. Bad cases: For 51: Pt4 and Pt14. For 92: M5 and M24.
#    (Bad case means there are images files loss or box outside the ROI)
#
# 2. Some suspicious cases listed in suspicious summary file
#    (Suspicious case means those ROI positions are suspicious and pending to be used for future)


# Note:
# 1. CEDM_51_TA and CEDM_92_TA 2 files and main features files. Later we add 2 raw features: Kurtosis and skewness
#    in Update_CEDM_51_TA and Update_CEDM_92_TA files
#
# 2. ROI_ShapeAnalysis_51 and 92 files can be removed from features files if not wanted.
#
