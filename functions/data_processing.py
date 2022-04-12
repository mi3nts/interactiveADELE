# CODE TO PROCESS RAW BIOMETRIC DATA

# CODE AUTHORED BY: SHAWHIN TALEBI
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - vhdr_fname = string. path to relevant .vhdr file
#       ~ example: vhdr_fname = "./data/2020_06_04_T05_U00T_EEG01.vhdr"
#   - var_name = string. name of biometric variable on which to base epoch detection
#   - num_bins  = number of bins the epoch should be split into

# OUTPUTS
#   - epoch_dict = dictionary where key is epoch number and value is a list containing the epoch edges.
#   ~ example: {'1': [0, 99], '2': [100, 150]} dictionary with 2 epochs, where the first epoch spans the first hundred records of x and the second spans the next 51.

# ADELE DEPENDENCIES
#   - read_eeg()
#   - decisionTree_epochDetection()
#   - getEpochbm_dict()

# ADELE DEPENDERS
#   - none

# ==============================================================================
from read_eeg import *
from decisionTree_epochDetection import *
from getEpochbm_dict import *

import numpy as np

def data_processing(vhdr_fname, var_name, num_bins):
    # READ DATA (EEG AND HR)
    eeg_data = read_eeg(vhdr_fname)

    # GET EPOCHS
    # define input data
    X = (np.vstack((np.arange(len(eeg_data)), eeg_data[var_name]))).transpose()
    # get epoch information as dictionary
    epoch_dict = decisionTree_epochDetection(num_bins, X)

    # GET FINAL DICTIONARY
    # get dictionary with epoch information and eeg bands
    epochbm_dict = getEpochbm_dict(eeg_data, epoch_dict)

    return epochbm_dict, epoch_dict

"""
# EXAMPLE
# define input vhdr filename
vhdr_fname = 'assets/data/2020_06_04_T05_U00T_EEG01/2020_06_04_T05_U00T_EEG01.vhdr'
# define input vhdr filename
var_name = 'HR'
# define number of bins
num_bins = 5

# perform data processing: get data dictionary from raw data
epochbm_dict = data_processing(vhdr_fname, var_name, num_bins)
print(epochbm_dict)
"""
