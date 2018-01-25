import dicom as pydicom
import os
from glob import glob
from natsort import natsorted, ns

# Set root_folder to path of DOI folder of XNAT data
root_folder = '/media/DataDisk/TCIA_LGG/DOI'
# Output folder for sorted data
out_dir = '/media/DataDisk/TCIA_LGG/Processed_T1T2'

patient_folders = glob(os.path.join(root_folder, '*' + os.pathsep))

for i_patient_folder in patient_folders:
    patient_ID = os.path.basename(os.path.normpath(i_patient_folder))
    sub_folder = glob(os.path.join(i_patient_folder, '*' + os.pathsep))
    scan_folders = glob(os.path.join(sub_folder[0], '*' + os.pathsep))

    for i_scan_folder in scan_folders:
        dicoms = glob(os.path.join(i_scan_folder, '*.dcm'))
        dicoms = natsorted(dicoms, alg=ns.IGNORECASE)

        for i_index, i_dicom in enumerate(dicoms):
            dicom_info = pydicom.read_file(i_dicom)

            if i_index == 0:
                repetition_time = dicom_info[0x18, 0x80].value
                if repetition_time > 1000:
                    scan_type = 'T2'
                    scan_number = '2'

                else:
                    scan_type = 'T1'
                    scan_number = '1'

            dicom_info[0x8, 0x103e].value = scan_type
            dicom_info[0x20, 0x11].value = scan_number

            save_dir = os.path.join(out_dir, patient_ID, scan_type)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            save_name = os.path.join(save_dir, str(i_index).zfill(5) + '.dcm')
            dicom_info.save_as(save_name)
