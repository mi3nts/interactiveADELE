# CODE TO FIND BRAINWAVES BANDS FOR ELECTRODES IN EACH EPOCH

# CODE AUTHORED BY: ROLANDO MARTINEZ
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - eeg_data = pandas dataframe with columns as biometric variables and rows
#   as timesteps
#   - epoch_dict = dictionary where keys are integers corresponding to each
#   epoch, and values are epoch time index ranges

# OUTPUTS
#   - epochbm_dict = dictionary with keys as integers corresponding to each epoch,
#   and values are a list containing epoch time index ranges and a pandas dataframe
#   where the rows are electrodes and columns are brainwaves bands for the given epoch

# ADELE DEPENDENCIES
#   - none

# ADELE DEPENDERS
#   - none
# ==============================================================================

# import modules
import mne
import numpy as np
import pandas as pd

# import functions
from scipy import signal


# define function
def getEpochbm_dict(eeg_data, epoch_dict):

    df = eeg_data.iloc[:, 0:64]     # create dataframe for 64 signals
    fs = 500                        # Sampling rate of 500 Hz
    epochbm_dict = dict()           # final dictionary

    # Define EEG frequency bands
    bands = {'Delta': (1, 3),
             'Theta': (4, 7),
             'Alpha': (8, 12),
             'Beta': (13, 25),
             'Gamma': (26, 45)}

    # Outer loop iterates through epoch dictionary and creates a dataframe for
    # each epoch based on its time index range and stores it along with the index
    # ranges in the final dictionary
    for e in epoch_dict:
        start_idx = epoch_dict[e][0]    # beginning time index range
        end_idx = epoch_dict[e][1]      # ending time index range

        eeg_list = []                   # list of band dictionaries
        idx_name = []                   # name of electrodes

        # slice dataframe according to epoch edges
        epoch_df = df[start_idx:end_idx]

        # inner loop goes through each column of the sliced dataframe applies the
        # welch function and stores the dictionaries in a list
        for i in epoch_df:
            idx_name.append(i)          # store name of electrode
            eeg_bands = dict()          # dictionary holding EEG bands as keys and freq as value

            # Take one electrode at a time from dataframe
            data_col = epoch_df.loc[:, i]
            eeg_signal = data_col.values

            # welch function applied to each electrode using sampling rate
            freq_arr, psd_arr = signal.welch(eeg_signal, fs)

            # find freq bands of all electrodes for given epoch and store in dictionary
            for b in bands:
                # Find frequency match with EEG bands
                freq_ix = np.where((freq_arr >= bands[b][0]) & (freq_arr <= bands[b][1]))

                # Calculate the mean of power spectrum value
                eeg_bands[b] = np.mean(psd_arr[freq_ix])

            # add band dictionary to list of dictionaries
            eeg_list.append(eeg_bands)

        # create new dataframe for freq bands of each electrode for given epoch
        bands_df = pd.DataFrame(eeg_list, columns=['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma'], index=idx_name)

        # add time index ranges and dataframe to dictionary in given epoch
        epochbm_dict[e] = [[start_idx, end_idx], bands_df]

    return epochbm_dict