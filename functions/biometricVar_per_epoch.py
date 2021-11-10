# CODE TO DERRIVE ROLLING AVERAGED BIOMETRIC VARIABLE(S) VALUE PER TIMESTEP PER EPOCH

# CODE AUTHORED BY: CHISOM SOPURUCHI	
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - epoch_dict = dictionary where keys are integers corresponding to each epoch, and values are epoch time index ranges
#   - eeg_data = pandas dataframe with columns as biometric variables and rows as timesteps
 
# OUTPUTS
#   - epochbm_dict = dictionary where keys are integers corresponding to each epoch and values are a list containing both epoch time index ranges and a pandas dataframe where rows are timesteps, and 1 column is heart value with rolling average.
#   ~ example: {'1': [[0, 99], dataframe], '2': [[100, 150], dataframe]} dictionary with 2 epochs, where the first epoch spans the first hundred records of x, the second spans the next 51. Dataframe represents a pandas data frame with index as the records and columns as pre-determined rolling averaged biometric variables spanned by each epoch.
#   ~ example: {'1': [[0, 99], dataframe]}, If the pre-determined biometric variable was 'HR', then the dataframe would have as index 0-99 and as columns, rolling averaged HR spanning index(0-99) in the input dataframe (eeg_data).  

# ADELE DEPENDENCIES
#   - none

# ADELE DEPENDERS
#   - none
# ==============================================================================

def biometricVar_per_epoch(epoch_dict, eeg_data):
    #import library
    import pandas as pd
    
    # define output dictionary
    epochbm_dict={}
    # list to store column names we want to access from the dataframe
    df_cols = ['HR', 'Temp.', 'SpO2']
    # apply rolling average to dataframe comprising of df_cols 
    rolled_df = eeg_data.loc[:,df_cols].rolling(window=5000).mean()
    # populate the output dictionary
    for key, value in epoch_dict.items():
        epochbm_dict[key]=[epoch_dict[key],rolled_df.loc[range(value[0], value[1])]]
        
    return epochbm_dict

