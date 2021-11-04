# CODE TO DISPLAY THE INTERACTIVE DASHBOARD

# CODE AUTHORED BY: ARJUN SRIDHAR
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - None
# OUTPUTS
#   - app - Plotly Dash app with interactive dashboard

# ADELE DEPENDENCIES
#   - brain_visual3
#   - Create_Slider_fn
#   - data_processing
#   - graph_biometric

# ADELE DEPENDERS
#   - none
# ==============================================================================

# import statements
import dash
from dash import html
from dash import dcc
import brain_visual3 as b3
import Create_Slider_fn as cs
import data_processing as dp
import pandas as pd
import plotly.graph_objs as go


# function that returns a figure with the biometric graph
# INPUTS - the dataframe and biometric to be graphed - string, i.e HR or SpO2, and epochbm dict
# OUTPUTS - the graph 
def graph_biometric(df, biometric, epochbm_dict):
    df_hr = df[biometric]
    df_hr_epoch_1 = df_hr[epochbm_dict['1'][0][0]:epochbm_dict['1'][0][1]]
    hr_epoch = df_hr_epoch_1.to_numpy()

    fig = go.Figure(data=[go.Scatter(x=list(range(len(hr_epoch))), y=hr_epoch)])
    fig.update_layout(
        title="%s for Epoch 1" %(biometric),
        title_x=0.5,
        xaxis_title="Time",
        yaxis_title=biometric,

    )
    graph = dcc.Graph(figure=fig)
    return graph


# function that returns a figure with the biometric graph for a selected epoch
# INPUTS - the dataframe and biometric to be graphed - string, i.e HR or SpO2, and epochbm dict
#           and epoch as an int
# OUTPUTS - the figure
def graph_biometric_selection(df, biometric, epochbm_dict, epoch):
    epoch = str(epoch)
    df_hr = df[biometric]
    df_hr_epoch_x = df_hr[epochbm_dict[epoch][0][0]:epochbm_dict[epoch][0][1]]
    hr_epoch = df_hr_epoch_x.to_numpy()

    fig = go.Figure(data=[go.Scatter(x=list(range(len(hr_epoch))), y=hr_epoch)])
    fig.update_layout(
        title="%s for Epoch %s" % (biometric, epoch),
        title_x=0.5,
        xaxis_title="Time",
        yaxis_title=biometric
    )
    return fig


def interactive_dashboard():
    df1 = pd.read_csv('./assets/data/sampleDataBM.csv')  # dummy data for now
    df1 = df1.dropna()

    # define input vhdr filename
    vhdr_fname = './assets/data/2020_06_04_T05_U00T_EEG01/2020_06_04_T05_U00T_EEG01.vhdr'
    # define input vhdr filename
    var_name = 'HR'
    # define number of bins
    num_bins = 5
    # perform data processing: get data dictionary from raw data
    epochbm_dict = dp.data_processing(vhdr_fname, var_name, num_bins)

    # Secondary component that determines what coordinate to plot
    mycheckbox = dcc.Checklist(
        id='checklist-for-graph',
        options=[
            {'label': 'Fp1', 'value': 'Fp1'},
            {'label': 'Fp2', 'value': 'Fp2'},
            {'label': 'F3', 'value': 'F3'},
        ],
        value=['Fp1', 'Fp2', 'F3']
    )
    # get slider with epochs
    slider = cs.create_slider(epochbm_dict)
    # Filepath of nii file from assets folder in the same directory
    img_file = "assets/BraTS19_2013_10_1_flair.nii"  # read in nii file from assets folder in same directory
    # Get the file of the cartesian coordinates
    filepath_name = 'assets/EEG01_chanlocs_cartesian.txt'

    # get visual parts
    data_brain, df, brain_fig = b3.brain_visual3(img_file, filepath_name, mycheckbox, 'value')

    # external stylesheet for format
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    # main application
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(children=[
        html.Div([  # upper row with brain and hr plot
            html.Div([
                html.Div([
                    mycheckbox,
                ]),
                html.Div([
                    dcc.Graph(
                        id="image-display-graph-3d",
                        config=dict(displayModeBar=False),
                        # figure=fig
                    ),
                ]),
            ], className='six columns'),
            html.Div([
                dcc.Graph(id='hr-graph1')
            ], className='six columns'),
        ], className='row'),
        html.Div([  # bottom row with just spo2 plot for now
            html.Div([
                dcc.Graph(id='SpO2-graph1')
            ], className='six columns'),
        ], className='row'),

        slider
    ])

    # Updates 3d brain when callback_object1 is changed
    @app.callback(
        dash.dependencies.Output('image-display-graph-3d', 'figure'),
        dash.dependencies.Input(mycheckbox.id, 'value')
    )
    def update_graph(selected_value):
        fig = b3.make_3d_fig(data_brain, df, selected_value)
        return fig

    # Updates hr plot when the slider is changed
    @app.callback(
        dash.dependencies.Output('hr-graph1', 'figure'),
        dash.dependencies.Input(slider.id, 'value')
    )
    def update_graph1(selected_value):
        fig = graph_biometric_selection(df1, 'HR', epochbm_dict, selected_value)
        return fig

    # Updates SpO2 plot when the slider is changed
    @app.callback(
        dash.dependencies.Output('SpO2-graph1', 'figure'),
        dash.dependencies.Input(slider.id, 'value')
    )
    def update_graph1(selected_value):
        fig = graph_biometric_selection(df1, 'SpO2', epochbm_dict, selected_value)
        return fig

    app.run_server(debug=True)


interactive_dashboard()
