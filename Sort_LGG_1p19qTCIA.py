import yaml
import Sort.Sort_Dicoms as SD
import os

with open('config.yaml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

data_folder = cfg['folders']['data_folder']

processed_data_folder = os.path.join(data_folder, 'Sorted_Data')

if not os.path.exists(processed_data_folder):
    os.makedirs(processed_data_folder)


dicom_folder = os.path.join(data_folder, 'DOI')
processed_data_dicom_folder = os.path.join(processed_data_folder, 'DICOM')

# Start by sorting the dicoms

T2_min_repetition_time = cfg['MR']['T2_min_repetition_time']
T2_min_echo_time = cfg['MR']['T2_min_echo_time']

SD.sort_dicoms_to_structured_folder(dicom_folder, processed_data_dicom_folder,
                                    T2_min_repetition_time,
                                    T2_min_echo_time)
