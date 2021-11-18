# CODE TO RETURN A DICTIONARY CONTAINING THE EPOCHS AS KEYS AND A LIST OF BOUNDARIES AND DATA AS THE VALUES.

# CODE AUTHORED BY: OMAR LUNA
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   -tobii_data: pandas Dataframe with timestamp values as the index and pupil diameter data as the columns
#   -epoch_dict: dictionary with predetermined epochs
#   -eeg_ts: timestamp from tobii device
# OUTPUTS
#   -epochbm_dict: dictionary where keys are integers corresponding to epochs and values are a list containing the epoch boundaries
#                   and the pupil diameter data within the boundaries of each epoch.

# ADELE DEPENDENCIES
#   - decisionTree_epochDetection
#   -getEpochbm_dict
#   -js_pupil_diameter
#   -read_eeg

# ADELE DEPENDERS
#   - none
# ==============================================================================

from read_eeg import *
from decisionTree_epochDetection import *
from getEpochbm_dict import *
from js_pupil_diameter import *
import numpy as np

def pd_epoch_dict(tobii_data, epoch_dict, eeg_filename):
     # Retrieve the eeg data timestamp from the file
    with open(eeg_filename) as f:
      lines = f.readlines()
    for i, line in enumerate(lines):
      ss_index = line.find('Recording Start Time')
      if ss_index > -1:
        # Store timestamp
        eeg_ts = lines[i+1]    
    eeg_ts = eeg_ts.replace('\n', '')
    dt_timestamp = dt.strptime(eeg_ts, "%Y-%m-%d %H:%M:%S.%f" )
    y = int(round(dt_timestamp.timestamp()))
    # list containing converted epoch timestamps
    l_epoch_ts = []
    # list cointaining data from tobii dataframe
    l_list = []
    # list containing epoch and data tuples
    l_tps = []

    # Loop to traverse epoch values
    for k in epoch_dict.values():
        x = k
        # converts epoch boundaries to datetime and stores in l_epoch_ts
        # timestamp / 500 = conversion from 500hz to seconds
        x[0] = dt.fromtimestamp((x[0]/500)+y)
        x[1] = dt.fromtimestamp((x[1]/500)+y)
        l_epoch_ts.append(x)

        # Loop to traverse values in tobii_data
        for i, df_item in enumerate(tobii_data.index.values):

            # Converts from numpy.datetime to datetime.datetime
            data_df_ts = dt.utcfromtimestamp(df_item.astype('O')/1e9)

            # Compares the index timestamp to the epoch boundaries
            if data_df_ts >= x[0] and data_df_ts <= x[1]:

                data_row = tobii_data.iloc[i,:]
                # stores rows of data into l_list
                l_list.append(data_row)

        # Create the epoch boundaries and dataframe values tuple
        tp = tuple(zip(l_epoch_ts + l_list))
        # add tuple to tuple list
        l_tps.append(tp)
        # clear lists used
        l_list.clear()
        l_epoch_ts.clear()
    epochbm_dict = dict(zip(epoch_dict.keys(), l_tps))

    # Returns dictionary
    return epochbm_dict
