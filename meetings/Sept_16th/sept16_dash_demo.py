# CODE TO DISPLAY DASH VISUALIZATION WITH MULTIPLE TABS
# CODE AUTHORED BY: ARJUN SRIDHAR
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - filepath = a string filepath to the relavant csv file with the data
#   - app = the dash application 

# OUTPUTS
#   - eeg_data = pandas dataframe with columns as biometric variables and rows as
#   timesteps

# ADELE DEPENDENCIES
#   - none

# ADELE DEPENDERS
#   - none
# ==============================================================================

# import libraries
import dash
import dash_core_components as dcc
from dash import html
import pandas as pd

# funnction that takes in a dash app and filepath and creates multiple tabs in the visualization
def sept16_demo(app, filepath):
    df = pd.read_csv(filepath) # read in csv to pandas dataframe
    
    # create app layout
    app.layout = html.Div([ # div structure for entire layout
        dcc.Tabs([ # create first tab
            dcc.Tab(label='HR Plot for Scrolling Twitter', children=[ # title of tab
                dcc.Graph( # graph structure to plot timeseries data
                    figure={
                        'data':[ # data to plot
                            { 'x': df['Datetime'], 'y': df['HR'],
                                'type': 'line'}
                        ],
                        'layout':{ # set layout properties such as title of graph and axis labels
                            'title': 'HR Plot over time for Twitter Data',
                            'yaxis':{
                                'title': 'HR'
                            },
                        }
                            
                    }
                    
                )
            ]),
                    
            dcc.Tab(label='Arjun Blink and Picture', children=[ # create second tab
                html.Video(
                    controls = True,
                    id = 'movie_player',
                    # video location - for static content, needs to be in a directory called static 
                    # in same location as python file
                    src = './static/arjun_blink_vid.mp4',
                    style={'width': '50%','padding-left':'25%', 'padding-right':'25%'} # format video size, location, etc.
                ),
                html.Img(
                    id = 'arjun_img',
                    # image location - for static content, needs to be in a directory called static 
                    # in same location as python file
                    src = './static/image.jpg',
                    style={'width': '50%','padding-left':'25%', 'padding-right':'25%'} # format image size, location, etc.
                )
            ]),
        ])
    ])

# main function to run app
if __name__ == "__main__":
    filepath = 'C:/Arjun/UT_DALLAS/Graduate/Research/Data/2020_06_04_T05_U00T_ADELE.csv' # filepath of data - data should be a csv
    app = dash.Dash(__name__)
    sept16_demo(app, filepath)
    app.run_server(debug=True)
