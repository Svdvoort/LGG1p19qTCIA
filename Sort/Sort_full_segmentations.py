import os
from glob import glob
import shutil

root_dir = '/media/DataDisk/TCIA_LGG_TEST/segmentations_TCIA_1p19q_Marion'
out_dir = '/media/DataDisk/TCIA_LGG_TEST/Sorted_Data/NIFTI'

for root, dirs, files in os.walk(root_dir):
    if 'T2.nii.gz' in files:
        mask_file = glob(os.path.join(root, 'mask-*.nii.gz'))
        patient_ID = os.path.basename(os.path.normpath(root))

        if len(mask_file) > 0:
            mask_file = mask_file[0]
            out_file_name = os.path.join(out_dir, patient_ID, 'Full_segmentation.nii.gz')

            shutil.copy(mask_file, out_file_name)
