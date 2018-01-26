import os
from glob import glob
import shutil

# Fix inconsistent naming in segmentation files

# Set root_folder to path of DOI folder of XNAT data
root_folder = '/media/DataDisk/TCIA_LGG/NiFTiSegmentationsEdited'
# Output folder for sorted data
out_dir = '/media/DataDisk/TCIA_LGG/Processed_Segmentations'

patient_folders = glob(os.path.join(root_folder, '*' + os.path.sep))

for i_patient_folder in patient_folders:
    patient_ID = os.path.basename(os.path.normpath(i_patient_folder))
    print('Now processing: ' + patient_ID)

    T1_file = glob(os.path.join(i_patient_folder, '*T1*'))[0]
    T2_file = glob(os.path.join(i_patient_folder, '*T2*'))[0]
    Segmentation_file = glob(os.path.join(i_patient_folder, '*Seg*'))[0]

    out_patient_folder = os.path.join(out_dir, patient_ID)
    if not os.path.exists(out_patient_folder):
        os.makedirs(out_patient_folder)

    T1_out_file = os.path.join(out_patient_folder, 'T1.nii.gz')
    T2_out_file = os.path.join(out_patient_folder, 'T2.nii.gz')
    Segmentation_out_file = os.path.join(out_patient_folder,
                                         'Segmentation.nii.gz')

    shutil.copy(T1_file, T1_out_file)
    shutil.copy(T2_file, T2_out_file)
    shutil.copy(Segmentation_file, Segmentation_out_file)
