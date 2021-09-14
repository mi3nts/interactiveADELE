# CODE TO READ EEG FILE COLLECTED WITH THE COGNIONICS MOBILE-128 SYSTEM USING MNE

# CODE AUTHORED BY: SHAWHIN TALEBI
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - vhdr_fname = string. path to relevant .vhdr file
#   ~ example: vhdr_fname = "./data/2020_06_04_T05_U00T_EEG01.vhdr"

# OUTPUTS
#   - eeg_data = pandas dataframe with columns as biometric variables and rows as
#   timesteps

# ADELE DEPENDENCIES
#   - none

# ADELE DEPENDERS
#   - none
# ==============================================================================

# import libraries
import mne
import pandas as pd

# define function
def read_eeg(vhdr_fname):
    # define list of indicies for non-eeg channels
    misc_list = []
    for i in range(18):
        misc_list.append(i+64)

    # read raw data
    raw = mne.io.read_raw_brainvision(vhdr_fname, misc=misc_list, preload=True,
        verbose=False)
    raw.info['line_freq'] = 500.

    # Set montage
    montage = mne.channels.make_standard_montage('easycap-M1')
    raw.set_montage(montage, verbose=False)

    # Set common average reference
    raw.set_eeg_reference('average', projection=False, verbose=False)

    # create pandas dataframe with eeg data
    eeg_data = pd.DataFrame(raw.get_data().transpose(), columns=raw.ch_names)

    return eeg_data
