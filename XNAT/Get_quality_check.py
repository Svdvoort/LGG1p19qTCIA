import XNATExplorer

xnat_root = 'https://bigr-rad-xnat.erasmusmc.nl/'
project_name = 'TCIA-LGG-1p19q'
out_file = '/media/DataDisk/TCIA_LGG_TEST/quality_check.csv'

explorer = XNATExplorer.XNATExplorer(xnat_root, project_name)

subjects = explorer.get_subjects()

N_total = 0.0
N_correct = 0.0
N_incorrect = 0.0
N_correct_deleted = 0.0
N_correct_not_deleted = 0.0
N_incorrect_deleted = 0.0
N_incorrect_not_deleted = 0.0
N_total_deleted = 0.0
N_total_not_deleted = 0.0

with open(out_file, 'w') as the_file:
    the_file.write('Patient_ID\tQuality\tComments\n')
    for i_subject in subjects:
        print(i_subject['label'])
        experiments = explorer.get_experiments(i_subject)
        i_experiment = experiments[0]

        experiment_resources = explorer.get_selected_experiment_resource_list(i_subject, i_experiment, 'FIELDS', 'quality_Marion')

        quality_results = explorer.get_experiment_resource(i_subject, i_experiment, 'FIELDS', experiment_resources[0]['Name'])
        to_write_string = i_subject['label'] + '\t' + quality_results['Quality'] + '\t' + quality_results['Quality_comments'] + '\n'
        the_file.write(to_write_string)
