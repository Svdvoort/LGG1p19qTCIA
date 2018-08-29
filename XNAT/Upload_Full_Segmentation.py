import XNATExplorer
import os


# Specificy xnat url
xnat_root = 'http://bigr-rad-xnat.erasmusmc.nl/'
project_name = 'LGG1p19qTCIA'

# Path to segmentation folder
segmentation_folder = '/media/DataDisk/TCIA_LGG_TEST/Sorted_Data/NIFTI'


def upload_nifti(subject_XNAT, scan_sequence, nifti_file, XNAT_folder, XNAT_name):
    experiment = explorer.get_experiments(subject_XNAT)[0]
    scan = explorer.find_scan(subject_XNAT, experiment, scan_sequence)[0]

    explorer.upload_scan_resource(subject_XNAT, experiment, scan, XNAT_folder,
                                  XNAT_name, nifti_file)
    return

explorer = XNATExplorer.XNATExplorer(xnat_root, project_name)


XNAT_subjects = explorer.get_subjects()

for i_subject in XNAT_subjects:
    subject_ID = i_subject['label']
    print(subject_ID)
    subject_folder = os.path.join(segmentation_folder, subject_ID)
    segmentation_file = os.path.join(subject_folder, 'Full_segmentation.nii.gz')
    if os.path.exists(segmentation_file):
        upload_nifti(i_subject, 'T2', segmentation_file, 'REGISTERED', 'full_segmentation.nii.gz')
