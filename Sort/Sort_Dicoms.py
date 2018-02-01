import dicom as pydicom
import os
from glob import glob
from natsort import natsorted, ns


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


def sort_dicoms_to_structured_folder(dicom_dir, out_dir,
                                     T2_min_repetition_time,
                                     T2_min_echo_time):
    patient_folders = glob(os.path.join(dicom_dir, '*' + os.path.sep))

    for i_patient_folder in patient_folders:
        patient_ID = os.path.basename(os.path.normpath(i_patient_folder))

        print('Now processing: ' + patient_ID)
        # Patient 766 has two folders instead of one, however second folder
        # only has one scan, so we can ignore it
        if patient_ID == 'LGG-766':
            correct_folder = '1.3.6.1.4.1.14519.5.2.1.3344.2526.158062589977495723809897712484'
            sub_folder = os.path.join(i_patient_folder, correct_folder)
        else:
            sub_folder = glob(
                os.path.join(i_patient_folder, '*' + os.path.sep))[0]

        scan_folders = glob(
                        os.path.join(sub_folder, '*' + os.path.sep))

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
                            scan_type = 'Proton_Density'
                            scan_number = '3'

                            series_UID = str(dicom_info[0x20, 0xe].value)
                            last_number_UID = int(series_UID[-1])

                            series_UID = series_UID[:-2]
                            series_UID = series_UID + str(last_number_UID + 1)
                            dicom_info[0x20, 0xe].value = series_UID

                        save_dir = os.path.join(out_dir, patient_ID, scan_type)
                        slice_number = len(glob(
                            os.path.join(save_dir, '*.dcm')))
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
