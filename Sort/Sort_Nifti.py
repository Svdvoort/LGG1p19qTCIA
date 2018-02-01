import os
from glob import glob
import shutil
import zipfile


def sort_nifti_files(data_folder, out_folder):
    nifti_zip = os.path.join(data_folder, 'NiFTiSegmentationsEdited.zip')

    zip_ref = zipfile.ZipFile(nifti_zip, 'r')
    zip_ref.extractall(data_folder)
    zip_ref.close()
    nifti_data_folder = os.path.join(data_folder, 'NiFTiSegmentationsEdited')
    patient_folders = glob(os.path.join(nifti_data_folder, '*' + os.path.sep))

    for i_patient_folder in patient_folders:
        patient_ID = os.path.basename(os.path.normpath(i_patient_folder))
        print('Now processing: ' + patient_ID)

        T1_file = glob(os.path.join(i_patient_folder, '*T1*'))[0]
        T2_file = glob(os.path.join(i_patient_folder, '*T2*'))[0]
        Segmentation_file = glob(os.path.join(i_patient_folder, '*Seg*'))[0]

        out_patient_folder = os.path.join(out_folder, patient_ID)
        if not os.path.exists(out_patient_folder):
            os.makedirs(out_patient_folder)

        T1_out_file = os.path.join(out_patient_folder, 'T1.nii.gz')
        T2_out_file = os.path.join(out_patient_folder, 'T2.nii.gz')
        Segmentation_out_file = os.path.join(out_patient_folder,
                                             'Segmentation.nii.gz')

        shutil.copy(T1_file, T1_out_file)
        shutil.copy(T2_file, T2_out_file)
        shutil.copy(Segmentation_file, Segmentation_out_file)
