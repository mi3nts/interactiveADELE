# interactiveADELE
Biometric project for F21 Senior Design Team

## Data Processing

### EEG Data
The EEG data consisted of 64 electrodes where each electrode had a specific voltage that was measured from the subject over time. The goal was to split that data into epochs and be able to show the EEG frequency bands of all the electrodes in each given epoch along with their respective time indices at which the data was split. To gain a better understanding of this EEG data the signal.welch function from the SciPy library was used on each electrode to convert the voltages to frequencies and collect the power spectral density. The frequencies were then matched to the corresponding EEG frequency bands of Delta, Theta, Alpha, Beta, and Gamma. Once a match was found the mean of the power spectral density for the electrode was taken to give the correct value for the given EEG frequency band. This process continued through each electrode where the end result was a dataframe consisting of all 64 electrodes and their respective frequency bands at each given epoch.

### Merging the data
Once all the data had been collected, the getEpochbm_dict function was adjusted to merge the EEG biometrics, non-EEG biometrics and pupil data into a single dictionary. This was done by importing the necessary functions and calling them to retrieve the dictionaries for the non-EEG biometrics and the pupil data inside getEpochbm_dict. As the list of time indices and dataframes are added to the dictionary in each given epoch the non-EEG biometrics and pupil data are also appended to the list in order to merge all the data. 

### Tobii Data
The Tobii Pro Glasses 2 produce 2 JSON files that we use to retrieve data. The first file is the particpant.json file which contains general information about the person conducting the live data recording.This file is useful because it contains the intial timestamp when the device began recording. The second file is the livedata.json file. This file contains all of the data recorded from the device. We use the pupil diameter readings from this file. The device takes 100 measurements a second. In participant_filename, the lines are read from the file until a string is found in one of the lines. When the string is found, the offset is calculated to retrieve the timestamp in as a substring. From a string, the value can be converted into the UTC format. The key "pd" is searched for in the file containing the data. If the key is found, we know the data is pupil diameter data. The dictionary item is returned containing only the timestamp, pupil diameter, and which eye the data belongs to. The pupil diameter dictionary items are appended to list and used to create a dataframe which is transformed using pivot() to set the index as the "ts" column and the left and right eye pupil diameter values as the columns. The timestamp from the pupil diameter data is offset by the timestamp in participant_filename and incremented by 1/100 of a second for every reading. This dataframe now contains the timestamps in UTC format, the left and right pupil diameters, the left and right values for the pupil diameter, and the average pupil diameter.

## Design and Development

### Slider
The slider is a tool being used to easily traverse between the different epochs being explored. The slider shows 5 different epochs that work with the graphs presented to relay different information regarding the HR and SpO2 levels while showing the correlating high activity electrodes on the brain. 

### Graphs
The graphs display the heart rate and oxygen saturation over an epoch period. The time range and data being shown depends on the epoch chosen.

### Brain Visualization
The brain visualization connects to the biometric data and the different epochs present in the slider to provide a visual on which areas of the brain show the most activity at the selected epoch. There are currently Theta and Alpha frequency band visuals for the brain which show the three highest activity electrodes for each.

![demo](docs/demo.gif)
