import ijroi
import numpy as np

rootDir = '/Users/yanzhexu/Desktop/Research/GBM/aCGH_whole_tumor_maps_for_Neuro-Onc_dataset/CEFSL_slices_only/slice22/ROI for +C_3D_AXIAL_IRSPGR_Fast_IM-0005-0022.roi'


with open(rootDir,"rb") as file:
    roi = ijroi.read_roi(file)

print isinstance(roi, np.ndarray)