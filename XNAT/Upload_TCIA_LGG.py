import XNATExplorer
import os
from glob import glob
import dicom as pydicom
import pandas as pd
from nipype.interfaces.dcm2nii import Dcm2nii


# Specificy xnat url
xnat_root = 'http://bigr-rad-xnat.erasmusmc.nl/'
project_name = 'LGG1p19qTCIA'

# Path to DICOM folder
DICOM_folder = '/media/DataDisk/TCIA_LGG/Processed_T1T2'
# Path to genetics excel
genetic_file = '/media/DataDisk/TCIA_LGG/TCIA_LGG_cases_159.xlsx'

explorer = XNATExplorer.XNATExplorer(xnat_root, project_name)

subject_folders = glob(os.path.join(DICOM_folder, '*/'))

genetics = pd.read_excel(genetic_file)
subject_names = genetics['Filename']
status_1p19q = genetics['1p/19q']
tumor_grade = genetics['Grade']
tumor_type = genetics['Type']

for i_index, i_subject in enumerate(subject_names):
    print(i_subject)
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
    age = dicom_loaded[0x10,0x1010].value[0:3]
    gender = dicom_loaded[0x10, 0x40].value

    explorer.set_gender(new_subject, gender)
    explorer.set_age(new_subject, age)

    explorer.set_custom_field(new_subject, 'deletion_1p', patient_1p_deletion)
    explorer.set_custom_field(new_subject, 'deletion_19q', patient_19q_deletion)
    explorer.set_custom_field(new_subject, 'grade', patient_grade)
    explorer.set_custom_field(new_subject, 'type', patient_type.lower())

    # explorer.upload_directory_to_prearchive(os.path.join(DICOM_folder, i_subject))

    T1_nifti_file = os.path.join(DICOM_folder, i_subject, 'T1.nii.gz')
    T2_nifti_file = os.path.join(DICOM_folder, i_subject, 'T2.nii.gz')

    T1_directory = os.path.join(DICOM_folder, i_subject, 'T1')
    T2_directory = os.path.join(DICOM_folder, i_subject, 'T2')

    converter = Dcm2nii()
    converter.inputs.source_dir = T1_directory
    converter.inputs.gzip_output = True
    converter.inputs.output_dir = T1_directory
    converter.inputs.source_in_filename = False
    converter.inputs.protocol_in_filename = False
    converter.inputs.date_in_filename = False
    converter.inputs.events_in_filename = False
    converter.inputs.id_in_filename = True
    convert_result = converter.run()

    T1_nifti_file = convert_result.outputs.converted_files
