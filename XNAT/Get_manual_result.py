import XNATExplorer
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn import metrics

xnat_root = 'https://bigr-rad-xnat.erasmusmc.nl/'
project_name = 'TCIA-LGG-1p19q'
file_name = 'Marion'
inclusion_list = '/media/DataDisk/TCIA_LGG_TEST/Included_patients_all.txt'
out_file = '/media/DataDisk/TCIA_LGG_TEST/Manual_classification_Marion.txt'

use_inclusion = True

explorer = XNATExplorer.XNATExplorer(xnat_root, project_name)

subjects = explorer.get_subjects()

N_total = 0.0
N_no_quality = 0.0

included_patients = np.loadtxt(inclusion_list, np.str)

y_truth = list()
y_prediction = list()
y_scores = list()

with open(out_file, 'w') as the_file:
    for i_subject in subjects:
        # print(i_subject['label'])

        if use_inclusion and i_subject['label'] in included_patients:
            experiments = explorer.get_experiments(i_subject)
            i_experiment = experiments[0]

            experiment_resources = explorer.get_selected_experiment_resource_list(i_subject, i_experiment, 'FIELDS', file_name)

            classification_results = explorer.get_experiment_resource(i_subject, i_experiment, 'FIELDS', experiment_resources[0]['Name'])

            real_label_1p = explorer.get_custom_field(i_subject, '1p_del')
            real_label_19q = explorer.get_custom_field(i_subject, '19q_del')

            if real_label_1p == 'true' and real_label_19q == 'true':
                real_label = 1
            else:
                real_label = 0
            y_truth.append(real_label)

            predicted_label = classification_results['1p19q_status']
            if predicted_label == 'Co-deleted':
                predicted_label = 1
            elif predicted_label == 'Not co-deleted':
                predicted_label = 0
            y_prediction.append(predicted_label)

            the_file.write(i_subject['label']+'\t'+str(predicted_label)+'\n')

            label_certainty = classification_results['Certainty']

            # Only if we have label certainty we use it
            if label_certainty:
                if predicted_label == 0:
                    y_score = -1.0 * float(label_certainty)/5.0
                elif predicted_label == 1.0:
                    y_score = 1.0 * float(label_certainty)/5.0
                y_scores.append(y_score)

            else:
                N_no_quality += 1
                y_scores.append(0)
                print(i_subject['label'])
                print(predicted_label)

            N_total += 1

print(y_scores)
c_mat = confusion_matrix(y_truth, y_prediction)
TN = float(c_mat[0, 0])
FN = float(c_mat[1, 0])
TP = float(c_mat[1, 1])
FP = float(c_mat[0, 1])

accuracy = (TP + TN)/(TP + TN + FP + FN)
sensitivity = TP/(TP+FN)
specificity = TN/(FP+TN)
precision = TP/(TP+FP)
f1 = f1_score(y_truth, y_prediction, average='weighted')

fpr, tpr, thresholds = metrics.roc_curve(y_truth, y_scores)
auc = metrics.auc(fpr, tpr)


print(N_total)
print(N_no_quality)

print("Accuracy:")
print(accuracy)

print("AUC:")
print(auc)

print("Sensitivity:")
print(sensitivity)

print("Specificity:")
print(specificity)

print("F1_score_weighted:")
print(f1)

print("Precision:")
print(precision)
