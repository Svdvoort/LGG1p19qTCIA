import dicom as pydicom
import os
from glob import glob
from natsort import natsorted, ns

# Set root_folder to path of DOI folder of XNAT data
root_folder = '/media/DataDisk/TCIA_LGG/DOI'
# Output folder for sorted data
out_dir = '/media/DataDisk/TCIA_LGG/Processed_T1T2'

T2_min_repetition_time = 1000
T2_min_echo_time = 50


def check_T2_and_PD(dicom_list):
    echo_times = list()

    for i_dicom in dicom_list:
        dicom_info = pydicom.read_file(i_dicom)
        echo_time = dicom_info[0x18, 0x81].value

        if echo_time not in echo_times:
            echo_times.append(echo_time)

        if len(echo_times) > 1:
            return True
    return False


patient_folders = glob(os.path.join(root_folder, '*' + os.path.sep))

for i_patient_folder in patient_folders:
    patient_ID = os.path.basename(os.path.normpath(i_patient_folder))
    print('Now processing: ' + patient_ID)
    sub_folder = glob(os.path.join(i_patient_folder, '*' + os.path.sep))
    scan_folders = glob(os.path.join(sub_folder[0], '*' + os.path.sep))

    for i_scan_folder in scan_folders:
        dicoms = glob(os.path.join(i_scan_folder, '*.dcm'))
        dicoms = natsorted(dicoms, alg=ns.IGNORECASE)

        for i_index, i_dicom in enumerate(dicoms):
            dicom_info = pydicom.read_file(i_dicom)

            repetition_time = dicom_info[0x18, 0x80].value
            echo_time = dicom_info[0x18, 0x81].value
            if repetition_time >= T2_min_repetition_time:
                is_T2_and_PD = check_T2_and_PD(dicoms)
                if not is_T2_and_PD:
                    scan_type = 'T2'
                    scan_number = '2'
                    slice_number = str(i_index).zfill(5)
                else:
                    if echo_time >= T2_min_echo_time:
                        scan_type = 'T2'
                        scan_number = '2'
                    else:
                        scan_type = 'PD'
                        scan_number = '3'

                        series_UID = str(dicom_info[0x20, 0xe].value)
                        last_number_UID = int(series_UID[-1])

                        series_UID = series_UID[:-2]
                        series_UID = series_UID + str(last_number_UID + 1)
                        dicom_info[0x20, 0xe].value = series_UID

                    save_dir = os.path.join(out_dir, patient_ID, scan_type)
                    slice_number = len(glob(os.path.join(save_dir, '*.dcm')))
                    slice_number = str(slice_number).zfill(5)

            else:
                scan_type = 'T1'
                scan_number = '1'
                slice_number = str(i_index).zfill(5)

            dicom_info[0x8, 0x103e].value = scan_type
            dicom_info[0x20, 0x11].value = scan_number

            save_dir = os.path.join(out_dir, patient_ID, scan_type)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            save_name = os.path.join(save_dir, slice_number + '.dcm')
            dicom_info.save_as(save_name)
