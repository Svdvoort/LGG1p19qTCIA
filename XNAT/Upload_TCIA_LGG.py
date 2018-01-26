import XNATExplorer
import os
from glob import glob
import dicom as pydicom
import pandas as pd
from nipype.interfaces.dcm2nii import Dcm2nii
import shutil

# Specificy xnat url
xnat_root = 'http://bigr-rad-xnat.erasmusmc.nl/'
project_name = 'LGG1p19qTCIA'

# Path to DICOM folder
DICOM_folder = '/media/DataDisk/TCIA_LGG/Processed_T1T2'
# Path to genetics excel
genetic_file = '/media/DataDisk/TCIA_LGG/TCIA_LGG_cases_159.xlsx'
# Path to segmentation folder
segmentation_folder = '/media/DataDisk/TCIA_LGG/Processed_Segmentations'


def make_and_upload_nifti(subject_name, subject_XNAT, scan_sequence):

    subject_directory = os.path.join(DICOM_folder, i_subject)
    dicom_directory = os.path.join(DICOM_folder, i_subject, scan_sequence)

    converter = Dcm2nii()
    converter.inputs.source_dir = dicom_directory
    converter.inputs.gzip_output = True
    converter.inputs.output_dir = subject_directory
    converter.inputs.source_in_filename = False
    converter.inputs.protocol_in_filename = False
    converter.inputs.date_in_filename = False
    converter.inputs.events_in_filename = False
    converter.inputs.id_in_filename = True
    converter.inputs.terminal_output = 'file'
    convert_result = converter.run()

    nifti_file = convert_result.outputs.converted_files

    shutil.move(nifti_file, os.path.join(subject_directory,
                                         scan_sequence + '.nii.gz'))
    nifti_file = os.path.join(subject_directory, scan_sequence + '.nii.gz')

    upload_nifti(subject_XNAT, scan_sequence, nifti_file, 'NIFTI', 'image.nii.gz')
    return


def upload_nifti(subject_XNAT, scan_sequence, nifti_file, XNAT_folder, XNAT_name):
    experiment = explorer.get_experiments(subject_XNAT)[0]
    scan = explorer.find_scan(subject_XNAT, experiment, scan_sequence)[0]

    explorer.upload_scan_resource(subject_XNAT, experiment, scan, XNAT_folder,
                                  XNAT_name, nifti_file)
    return

explorer = XNATExplorer.XNATExplorer(xnat_root, project_name)

subject_folders = glob(os.path.join(DICOM_folder, '*/'))

genetics = pd.read_excel(genetic_file)
subject_names = genetics['Filename']
status_1p19q = genetics['1p/19q']
tumor_grade = genetics['Grade']
tumor_type = genetics['Type']

for i_index, i_subject in enumerate(subject_names):
    print('Now processing: ' + i_subject)
    new_subject = explorer.create_subject(i_subject)

    # Find tumor genetics, grade and type from excel
    patient_1p19q_status = status_1p19q[i_index]
    patient_grade = tumor_grade[i_index]
    patient_type = tumor_type[i_index]

    patient_1p_deletion = patient_1p19q_status[0] == 'd'
    patient_19q_deletion = patient_1p19q_status[2] == 'd'

    # Get age and gender from dicom
    dicom_patient_folder = os.path.join(DICOM_folder, i_subject)
    dicom_file = os.path.join(dicom_patient_folder, 'T1', '00000.dcm')
    dicom_loaded = pydicom.read_file(dicom_file)
    age = dicom_loaded[0x10, 0x1010].value[0:3]
    gender = dicom_loaded[0x10, 0x40].value

    explorer.set_gender(new_subject, gender)
    explorer.set_age(new_subject, age)

    explorer.set_custom_field(new_subject, 'deletion_1p', patient_1p_deletion)
    explorer.set_custom_field(new_subject, 'deletion_19q', patient_19q_deletion)
    explorer.set_custom_field(new_subject, 'grade', patient_grade)
    explorer.set_custom_field(new_subject, 'type', patient_type.lower())

    explorer.upload_directory_to_prearchive(os.path.join(DICOM_folder, i_subject))

    explorer.archive_session()

    # Make nifti from the original DICOM
    make_and_upload_nifti(i_subject, new_subject, 'T1')
    make_and_upload_nifti(i_subject, new_subject, 'T2')
    if os.path.exists(os.path.join(DICOM_folder, i_subject, 'PD')):
        make_and_upload_nifti(i_subject, new_subject, 'PD')

    # Upload registered niftis, which were segmented
    T1_registered_nifti = os.path.join(segmentation_folder, i_subject,
                                       'T1.nii.gz')
    T2_registered_nifti = os.path.join(segmentation_folder, i_subject,
                                       'T2.nii.gz')
    Segmentation_registered_nifti = os.path.join(segmentation_folder, i_subject,
                                                 'Segmentation.nii.gz')

    upload_nifti(new_subject, 'T1', T1_registered_nifti, 'REGISTERED', 'image.nii.gz')
    upload_nifti(new_subject, 'T2', T2_registered_nifti, 'REGISTERED', 'image.nii.gz')
    upload_nifti(new_subject, 'T1', Segmentation_registered_nifti, 'REGISTERED', 'segmentation.nii.gz')
    upload_nifti(new_subject, 'T2', Segmentation_registered_nifti, 'REGISTERED', 'segmentation.nii.gz')
