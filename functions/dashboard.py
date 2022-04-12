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
#   - highest_electrodes

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
import highest_electrodes as he
import pandas as pd
import plotly.graph_objs as go


# function that returns a figure with the biometric graph for a selected epoch
# INPUTS - the dataframe and biometric to be graphed - string, i.e HR or SpO2, epochbm dictionary,
#           and epoch as an int
# OUTPUTS - the figure
def graph_biometric_selection(biometric, epochbm_dict, epoch):
    epoch = str(epoch)

    # Get the x values from the dictionary,
    #   numerate from each endpoint,
    #   and convert to seconds by dividing by 500
    x_values = epochbm_dict[epoch][0]
    x_values = list(range(x_values[0], x_values[1]))
    x_values = [number / 500 for number in x_values]

    # Get the y values from the dictionary
    y_df = epochbm_dict[epoch][2][biometric]
    y_values = y_df.values.tolist()

    fig = go.Figure(data=[go.Scatter(x=x_values, y=y_values)])
    fig.update_layout(
        title="%s for Epoch %s" % (biometric, epoch),
        title_x=0.5,
        xaxis_title="Time (sec)",
        yaxis_title=biometric
    )
    return fig


def interactive_dashboard():
    # df1 = pd.read_csv('./assets/data/sampleDataBM.csv')  # dummy data for now
    # df1 = df1.dropna()

    # define input vhdr filename
    vhdr_fname = './assets/data/2020_06_04_T05_U00T_EEG01/2020_06_04_T05_U00T_EEG01.vhdr'
    # define input vhdr filename
    var_name = 'HR'
    # define number of bins
    num_bins = 5
    # perform data processing: get data dictionary from raw data
    epochbm_dict = dp.data_processing(vhdr_fname, var_name, num_bins)

    # get slider with epochs
    slider = cs.create_slider(epochbm_dict)
    # Filepath of nii file from assets folder in the same directory
    img_file = "assets/BraTS19_2013_10_1_flair.nii"  # read in nii file from assets folder in same directory
    # Get the file of the cartesian coordinates
    filepath_name = 'assets/EEG01_chanlocs_cartesian.txt'

    # get visual parts
    data_brain, df = b3.brain_visual3(img_file, filepath_name)

    # external stylesheet for format
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    # main application
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(children=[
        # Top row title
        html.Div([
            html.H1(
                children=f"Trial: {'_'.join(map(str, vhdr_fname.split('/')[3].split('_')[:4]))}, epochs based on {var_name}",
                style={
                    'textAlign': 'center'})
        ]),
        # Second row slider
        html.Div([
            slider,
        ], style={
            'font-size': '12px',
            'font-color': 'blue',
            'padding': '10px',
        }),
        # Third row with brain and HR plot
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        id="image-display-graph-3d-1",
                        config=dict(displayModeBar=False),
                        style={
                            'margin-left': 100,
                            'display': 'inline-block'
                        })
                ]),
            ], className='six columns'),
            html.Div([
                dcc.Graph(id='hr-graph1',
                          style={
                              'display': 'inline-block'
                          })
            ], className='six columns'),
        ], className='row'),
        # Fourth row with brain and Sp02 plot
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        id="image-display-graph-3d-2",
                        config=dict(displayModeBar=False),
                        style={
                            'margin-left': 100,
                            'display': 'inline-block'}
                    )
                ])
            ], className='six columns'),
            html.Div([
                dcc.Graph(id='SpO2-graph1',
                          style={
                              'display': 'inline-block'
                          })
            ], className='six columns')
        ], className='row',
        ),

    ], style={'backgroundColor': 'gray',
              "border": "4px black solid"},
    )

    # Updates 3d brain 1 (Theta band) with the electrode to plot when slider is changed
    @app.callback(
        dash.dependencies.Output('image-display-graph-3d-1', 'figure'),
        dash.dependencies.Input(slider.id, 'value')  # for the electrode value
    )
    def update_graph(selected_value):
        high3 = he.highest_electrodes(epochbm_dict, selected_value, "Theta")
        fig = b3.make_3d_fig(data_brain, df, high3, "Theta")
        return fig

    # Updates 3d brain 2 (Alpha band) with the electrode to plot when slider is changed
    @app.callback(
        dash.dependencies.Output('image-display-graph-3d-2', 'figure'),
        dash.dependencies.Input(slider.id, 'value')  # for the electrode value
    )
    def update_graph(selected_value):
        high3 = he.highest_electrodes(epochbm_dict, selected_value, "Alpha")
        fig = b3.make_3d_fig(data_brain, df, high3, "Alpha")
        return fig

    # Updates hr plot when the slider is changed
    @app.callback(
        dash.dependencies.Output('hr-graph1', 'figure'),
        dash.dependencies.Input(slider.id, 'value')
    )
    def update_graph1(selected_value):
        fig = graph_biometric_selection('HR', epochbm_dict, selected_value)
        return fig

    # Updates SpO2 plot when the slider is changed
    @app.callback(
        dash.dependencies.Output('SpO2-graph1', 'figure'),
        dash.dependencies.Input(slider.id, 'value')
    )
    def update_graph1(selected_value):
        fig = graph_biometric_selection('SpO2', epochbm_dict, selected_value)
        return fig

    app.run_server(debug=True)


interactive_dashboard()
