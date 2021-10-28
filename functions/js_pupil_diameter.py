# CODE TO PARSE JSON FILE FOR PUPIL DIAMETER DATA

# CODE AUTHORED BY: OMAR LUNA
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   -participant json filename
#   -data json filename
# OUTPUTS
#   - pandas DataFrame containing the data for the left and right pupil diameter

# ADELE DEPENDENCIES
#   - none

# ADELE DEPENDERS
#   - none
# ==============================================================================

# Import libraries
import json as js
import pandas as pd
import numpy as np
from datetime import datetime as dt

# Function that returns pupil diameter data from a json file as a dataframe
def json_to_dataframe(participant_filename, data_filename):

  # function returns initial timestamp from participant.json file
  def get_ptimestamp(filename):
    with open(filename) as f:
      for i, line in enumerate(f):

        # find index of substring containing pa_created
        ss_index = line.find('pa_created')
        if ss_index > -1:

          # parse the timestamp and convert to datetime
          ts = line[ss_index+14: len(line)-2]
          dt_timestamp = dt.strptime(ts, "%Y-%m-%dT%H:%M:%S+%f" )
          return dt_timestamp

  def data_parsing(dict_data):

    # searches for pd key in dictionary
    if "pd" in dict_data:

      # removes keys not used and returns dictionary
      del dict_data["s"], dict_data["gidx"],
      return dict_data



  # Open file with data values and store them in list
  def get_data(filename, list_data):
    with open(filename) as f_livedata:
        for i, line in enumerate(f_livedata):
          p_data = data_parsing(js.loads(line))
          if p_data!=None:
            list_data.append(p_data)
          else:
            continue


  # list that contains pd data
  list_data = []
  # list that contains final datetime values
  l_final_ts = []

  # stores pd data in list_data from file
  get_data(data_filename, list_data)
  # returns initial timestamp from file
  p_ts = get_ptimestamp(participant_filename)
  # Creates initial dataframe
  df_pd = pd.DataFrame.from_dict(list_data)
  df_pd = df_pd.pivot(index='ts', columns= 'eye')

  # Converts initial datetime value to int
  timestamp = int(round(p_ts.timestamp()))
  # stores index values
  index_vals = df_pd.index.values
  # calculates the difference in seconds between values (1e6 = microseconds)
  step = (index_vals[1] - index_vals[0])/1e6

  # Converts int values to datetime values
  for i in range(0, index_vals.size, 1):
    l_final_ts.append(dt.fromtimestamp(timestamp + (i*step)))

  #final dataframe
  df_final = pd.DataFrame(df_pd.values, columns= df_pd.columns,  index=l_final_ts)
  return df_final
