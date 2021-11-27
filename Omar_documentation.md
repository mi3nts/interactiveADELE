# Functions

## pd_epoch_dict.py

### Inputs:

- tobii_data<br>
Pandas DataFrame containing the pupil diameter data with timestamp values as index.
- epoch_dict<br>
Dictionary with predetermined epochs and boundaries.
- eeg_filename<br>
The file containing the biometric data

### Outputs:

- epochbm_dict<br>
Dictionary containing the integer value of the epochs as keys and a list containing the epoch boundaries and pupil diameter data
as the values.

### Function description

The function takes in a dataframe from the json_to_dataframe function in Js_pupil_diameter.py. This dataframe contains the pupil data as well as the timestamps of the data.
This dataframe is used to store all the corresponding pupil data with the appropriate epoch boundaries detected. Epoch boundaries are timestamp boundaries determined by decisionTree_epochDetection
which returns a dictionary with predetermined epochs, epoch_dict, corresponding to the biometric data. The eeg_filename file is used to retrieve the initial biometric data timestamp.
The timestamp values from each epoch are converted into the datetime.datetime format and are appended to a list. Using these boundary pairs as the bounds for the data in tobii_data,
the values within the bounds are appended to a different list. Once the list of data is created for each epoch, a tuple is created containing the epoch boundary values and the data values.
Finally, a dictionary is created by using the keys from epoch_dict and the tuples containing the boundaries and data values. This dictionary is returned.


## Js_pupil_diameter.py

### Inputs:

- participant_filename<br>
JSON file produced by running an experiment with the Tobii Pro Glasses 2 containing the information regarding the individual using the device as well as information about recorded data.
- data_filename<br>
JSON file produced by running an experiment with the Tobii Pro Glasses 2 containing the data valuese recorded during the experiment.

### Outputs:

- df_final<br>
The pandas DataFrame containing the left, right, and average pupil diameters as columns and the timestamps of the data as index values.

### Description:

The json_to_dataframe() function retrieves the initial time of the recording from the participant_filename using the get_ptimestamp() function and
the data recorded from the experiment using the get_data() function. Once the data is stored, it is used to create a dataframe that is reshaped through DataFrame.pivot() which
sets the timestamp values as the index and the left and right pupil diameters as the columns. The initial time of recording is then converted into a timestamp value and used
to adjust the values in the DataFrame. A final DataFrame with the converted index values and the left, right, and average pupil diameters is returned.

### Sub-Functions:

- get_ptimestamp(filename)<br>
Function that returns the inital time of the recording from the participant_filename.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Inputs:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- filename<br>
JSON file produced by running an experiment with the Tobii Pro Glasses 2 containing the information regarding the individual using the device as well as information about recorded data.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Outputs:
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- dt_timestamp<br>
The initial time of recoding as a datetime.datetime object

#### Description:
The get_ptimestamp() function iterates through the lines in the filename file until it encounters a line containing
the string 'pa_created'. Once this string is found, the substring containing the timestamp is converted from a string to a datetime.datetime object and returned.

- data_parsing(dict_data)<br>
Function that searches for the 'pd' key inside of a dictionary.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Inputs:
- dict_data<br>
A dictionary item containing the data from one instance in the recording
#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Outputs:
- dict_data<br>
  The same dictionary is returned after the unused columns from data are removed.

#### Description:
A dictionary item is passed into the function. If there is pupil diameter data in that dictionary item,
the unused columns are deleted and the dictionary item is returned.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- get_data(filename, list_data)<br>
Function to store the values from the data_filename in a list.

#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Inputs:

- filename<br>
JSON file produced by running an experiment with the Tobii Pro Glasses 2 containing the data valuese recorded during the experiment.
- list_data<br>
List that contains the pupil diameter data from the filename file.

#### Description:

The get_data() function opens the filename file and iterates through the lines of the file. Every line is
passed into the data_parsing() function. If a dictionary item containing pupil data is returned, that item is stored into the list_data list.
If no dictionary item is returned, the loop continues to the next line in the file.

### Parsing Json file

To parse the Json file containing the live data, the initial determination to use a dictionary was made after using other data structures such as strings, lists, and dataframes. The issue that
arose using dataframes was that in order to access the end of the dataframe, a calculation, that increased in time as data grew, had to be made at each line read in from the file. However, a dictionary allowed for a faster copying process and a more mutable data strucute. The dictionary items returned by js.loads(string) were used
to search for the key "pd". If the key is found, we know the data is pupil diameter data. The uneccessary columns, column "s" and column "gidx", are removed from the dictionary item. The dictionary item is returned containing only the
timestamp, pupil diameter, and which eye the data belongs to. The pupil diameter dictionary items are appended to list and used to create a dataframe which is transformed using pivot() to set the index as the "ts" column and the left and right eye pupil diameter values as the columns.
The timestamp from the pupil diameter data is offset by the timestamp in participant_filename and incremented by 1/100 of a second for every reading. Both timestamps are pulled in a similar way from the files. In participant_filename, the lines are read from the file until a string is found in one of the lines. When the string is found,
the offset is calculated to retrieve the timestamp in as a substring. From a string, the value can be converted into the UTC format using strptime
