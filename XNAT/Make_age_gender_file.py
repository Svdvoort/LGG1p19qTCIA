import XNATExplorer

xnat_root = 'https://bigr-rad-xnat.erasmusmc.nl/'
project_name = 'LGG1p19qTCIA'
out_file = '/media/DataDisk/TCIA_LGG/age_gender.csv'

explorer = XNATExplorer.XNATExplorer(xnat_root, project_name)

subjects = explorer.get_subjects()

with open(out_file, 'w') as the_file:
    the_file.write('subject_ID\tage\tgender\n')
    for i_subject in subjects:
        subject_ID = i_subject['label']

        age = explorer.get_age(i_subject)
        gender = explorer.get_gender(i_subject)

        the_file.write(subject_ID + '\t' + str(age) + '\t' + str(gender) + '\n')
