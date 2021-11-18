# interactiveADELE
Biometric project for F21 Senior Design Team

## Data Processing

### EEG Data
The EEG data consisted of 64 electrodes where each electrode had a specific voltage that was measured from the subject over time. The goal was to split that data into epochs and be able to show the EEG frequency bands of all the electrodes in each given epoch along with their respective time indices at which the data was split. To gain a better understanding of this EEG data the signal.welch function from the SciPy library was used on each electrode to convert the voltages to frequencies and collect the power spectral density. The frequencies were then matched to the corresponding EEG frequency bands of Delta, Theta, Alpha, Beta, and Gamma. Once a match was found the mean of the power spectral density for the electrode was taken to give the correct value for the given EEG frequency band. This process continued through each electrode where the end result was a dataframe consisting of all 64 electrodes and their respective frequency bands at each given epoch.

### Merging the data
Once all the data had been collected, the getEpochbm_dict function was adjusted to merge the EEG biometrics, non-EEG biometrics and pupil data into a single dictionary. This was done by importing the necessary functions and calling them to retrieve the dictionaries for the non-EEG biometrics and the pupil data inside getEpochbm_dict. As the list of time indices and dataframes are added to the dictionary in each given epoch the non-EEG biometrics and pupil data are also appended to the list in order to merge all the data. 

![demo](docs/demo.gif)
