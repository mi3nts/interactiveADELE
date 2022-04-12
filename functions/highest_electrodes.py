# CODE TO SELECT THE THREE ELECTRODES WITH THE HIGHEST ACTIVITY

# CODE AUTHORED BY: MICHAEL LEE
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - epochbm_dict - dictionary of band data with epoch as the key
#   - epoch - epoch name to select
#   - band - frequency band name to select

# OUTPUTS
#   - electrode_list - descending list of the three electrodes with the highest values in the epoch and band

# ADELE DEPENDENCIES
#   - none

# ADELE DEPENDERS
#   - none
# ==============================================================================
def highest_electrodes(epochbm_dict, epoch, band, num_bins):
    # Get the correct dataframe for a certain epoch
    epoch = str(epoch)
    df = epochbm_dict[epoch][1][band]

    # Sort descending
    mylist = df.sort_values(ascending=False)

    # get the first 3 items of the list
    # get the index of the first 3 items of the list
    first3 = mylist[0:3:]
    electrode_list = first3.index.values

    full_event = []
    if band == 'Alpha':
        for i in range(1,num_bins+1):
            dummy_df = list(epochbm_dict[str(i)][1]['Alpha'].sort_values(ascending=False).iloc[0:3:].index.values)
            full_event.append(dummy_df)
            # print(dummy_df)
        # print(full_event)

    return electrode_list, full_event
