# CODE TO CREATE A SLIDER USING THE EPOCH TIMES 
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - epochs = the dictionary where the key is the epoch and the value is [start, end]
#   - example: {'1': [0, 99], '2': [100, 150]} dictionary with 2 epochs, where
#   the first epoch spans the first hundred records of x and the second spans
#   the next 51.

# OUTPUTS
#   - the slider with the epochs

import dash_html_components as html
import dash_core_components as dcc

def create_slider(epochs):
    slider = dcc.Slider() # ADD CODE TO CREATE SLIDER WITH EPOCHS
    
    return slider
    