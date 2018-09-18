import numpy as np

comparison_file = '/media/DataDisk/TCIA_LGG_TEST/Comparison_algorithm_Marion.txt'

comparisons = np.loadtxt(comparison_file, delimiter='\t', dtype=np.str)

true_label = comparisons[:, 1]
algorithm_label = comparisons[:, 2]
manual_label = comparisons[:, 3]
