rootDir = '/Users/yanzhexu/Google Drive/Marley Grant Data/CEDM pilot data-selected/malignant/Pt9/Pt9 - DES - CC.dcm';

I = dicomread(rootDir);

dim = size(I);

gs = I(899,4);

fprintf('%i\n', gs)