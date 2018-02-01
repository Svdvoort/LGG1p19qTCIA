import yaml
import Sort.Sort_Dicoms as SD
import Sort.Sort_Nifti as SN
import os

with open('config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

data_folder = cfg['folders']['data_folder']

processed_data_folder = os.path.join(data_folder, 'Sorted_Data')

if not os.path.exists(processed_data_folder):
    os.makedirs(processed_data_folder)


dicom_folder = os.path.join(data_folder, 'DOI')
processed_data_dicom_folder = os.path.join(processed_data_folder, 'DICOM')
processed_data_nifti_folder = os.path.join(processed_data_folder, 'NIFTI')

# Start by sorting the dicoms

T2_min_repetition_time = cfg['MR']['T2_min_repetition_time']
T2_min_echo_time = cfg['MR']['T2_min_echo_time']

print("Starting to sort and clean-up DICOM")
SD.sort_dicoms_to_structured_folder(dicom_folder, processed_data_dicom_folder,
                                    T2_min_repetition_time,
                                    T2_min_echo_time)
print("Starting to sort and clean-up NIFTI")
SN.sort_nifti_files(data_folder,
                    processed_data_nifti_folder)
