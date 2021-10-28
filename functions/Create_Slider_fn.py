# CODE TO CREATE A SLIDER USING THE EPOCH TIMES

# CODE AUTHORED BY: Nikhil John
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - epochs = the dictionary where the key is the epoch and the value is [start, end]

# OUTPUTS
#   - a slider with the epochs

# import libraries
import dash_core_components as dcc


# slider function
def create_slider(epoch_dict):
    slider_dict = {}  # dictionary
    for epoch in epoch_dict:  # loops over all keys in epoch dict
        slider_dict[epoch] = 'epoch {}'.format(epoch)  # displaying on the slider the epoch number (1-4)
    slider = dcc.Slider(  # characteristics of our slider here
        id='Epoch Slider',

        marks=slider_dict,

        step=None,
        min=1,
        max=len(slider_dict),  # the maximum is the total length of our slider dictionary (4)
        value=len(slider_dict),  # the length is the total length of our slider dictionary (4)

    )
    return slider
