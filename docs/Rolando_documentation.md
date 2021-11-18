# getEpochbm_dict(eeg_data, epoch_dict)

This Function is used to create a dictionary where the keys are the epoch integers from the epoch dictionary and the values are a list of time index ranges, EEG biometrics, non-EEG biometrics, and pupil data. 

## ADELE DEPENDENCIES
- biometricVar_per_epoch()
- js_pupil_diameter()
- pd_epoch_dict()

## ADELE DEPENDERS
- data_processing()

## INPUTS
- eeg_data

pandas dataframe with columns as biometric variables and rows as timesteps

- epoch_dict

dictionary where keys are integers corresponding to each epoch, and values are epoch time index ranges

## OUTPUTS
 - epochbm_dict
 
Dictionary with keys as integers corresponding to each epoch, and values are a list containing epoch time index ranges, a pandas dataframe where the rows are electrodes and columns are brainwaves bands for the given epoch, and another pandas dataframe containing non-eeg data where rows are time index and columns are the non-eeg biometric names.

Example of the format:
```sh
{1: [[start, end], eeg_bands, non_eeg_data]}.
```
## DESCRIPTION
The function begins by iterating through epoch_dict and identifying the starting and ending index for each epoch. The biometrics dataframe is then sliced according to the index values. Next, the signal.welch function is applied to each electrode in the sliced dataframe and the EEG bands dictionary is used to find the frequency bands for the electrodes. The frequency bands are then stored in a list that tracks all the labels for each electrode in each epoch. The dictionary list is then converted to a dataframe and added to the final epoch dictionary.
