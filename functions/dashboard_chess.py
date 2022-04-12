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
from cv2 import MARKER_SQUARE
import dash
from dash import html
from dash import dcc
import brain_visual3 as b3
import Create_Slider_fn as cs
import data_processing as dp
import highest_electrodes as he
import pandas as pd
import plotly.graph_objs as go
import audio_to_text as aud
import obj_detection as objs
import blink_detection as bd
import electrodeFunction as ef
import dash_player
from dash.dependencies import Input, Output
import numpy as np
from sklearn.ensemble import IsolationForest
from dash.exceptions import PreventUpdate
import os

if __name__ == "__main__":
    # function that returns a figure with the biometric graph
    # INPUTS - the dataframe and biometric to be graphed - string, i.e HR or SpO2, and epochbm dict
    # OUTPUTS - the graph
    def graph_biometric(df, biometric, epochbm_dict):
        df_hr = df[biometric]
        df_hr_epoch_1 = df_hr[epochbm_dict['1'][0][0]:epochbm_dict['1'][0][1]]
        hr_epoch = df_hr_epoch_1.to_numpy()

        fig = go.Figure(data=[go.Scatter(x=list(range(len(hr_epoch))), y=hr_epoch)])
        fig.update_layout(
            title="%s for Epoch 1" % biometric,
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
    def graph_biometric_selection(biometric, epochbm_dict, epoch):
        epoch = str(epoch)

        # Get the x values from the dictionary,
        #   numerate from each endpoint,
        #   and convert to seconds by dividing by 500
        x_values = epochbm_dict[epoch][0]
        x_values = list(range(x_values[0], x_values[1]))
        x_values = [number / 500 for number in x_values]

        y_df = epochbm_dict[epoch][2][biometric]
        y_values = y_df.values.tolist()

        fig = go.Figure(data=[go.Scatter(x=x_values, y=y_values)])
        fig.update_layout(
            title="%s for Epoch %s" % (biometric, epoch),
            title_x=0.5,
            xaxis_title="Time (sec)",
            yaxis_title=biometric,
            plot_bgcolor='rgb(11,82,91)',
            paper_bgcolor='rgb(27,58,75)',
            font_color="white"
        )
        return fig

    def blink_preprocess(df):

        # the function's purpose is to convert the original blink csv's timestamp into a readable format

        # get only the time portions from the timestamp
        time_all_unsplit = [i.split(" ")[1].split(":") for i in df['TimeStamp']]

        ts_corr = []
        for i in time_all_unsplit:
            if int(int(i[1]) < 1):
                ts_corr.append(float(i[2]))
            else:
                ts_corr.append(int(i[1])*60+float(i[2]))

        df['TS_corrected'] = ts_corr
        df = df.rename(columns={'Unnamed: 0': 'Ind'})

        return df

    def blink_isolation(df):

        # number of standard deviations away from the rolling mean 
        devs = 3

        # size of the rolling window
        roll_window = 100

        # duration to be classified as a blink, in multiples of 20, eg. dur=2 means >=60ms or ([2+1]*20) ms. Time resolution is 20 ms
        dur = 2

        # pot_outliers will contain points below 3 sigma away from rolling EAR_Avg 
        rolling = df['EAR_Avg'].rolling(roll_window).mean()
        rolling_std = rolling - devs*rolling.std()

        pot_outliers = df.loc[df['EAR_Avg'] < rolling_std]

        # a first order estimation of contamination, a ratio of data 3 sigma away from mean to total data
        contam = len(pot_outliers)/len(df)

        # implement isolation forest
        data_np = df['EAR_Avg'].to_numpy().reshape(-1,1)

        model = IsolationForest(n_estimators=100, max_samples='auto', contamination=contam, random_state=42)

        fit = model.fit(data_np)
        decision = model.decision_function(data_np)
        pred = model.predict(data_np)

        blinks_if_all = pd.DataFrame({'TS_corrected':df['TS_corrected'], 'Ind': df['Ind'], 'EAR_Avg':df['EAR_Avg'], 'IF_Class':np.where(pred == -1, 1, 0)})
        blinks_if = blinks_if_all[blinks_if_all['IF_Class'] == 1]
        blinks_if_mean_removed = blinks_if[blinks_if['EAR_Avg'] < blinks_if_all['EAR_Avg'].mean()]

        # pred_df = pd.DataFrame({'dec':decision, 'pred':pred})

        # ears = pd.DataFrame({'inds':pred_df.loc[pred_df['pred'] == -1].index, 'EAR_vals': df['EAR_Avg'][pred_df.loc[pred_df['pred'] == -1].index]})
        # mean_ears = ears['EAR_vals'].mean()
        # ears = ears[ears['EAR_vals'] < mean_ears]

        # ears['ts'] = [i/49.78 for i in ears['inds']]

        return blinks_if_mean_removed

    def graph_blinks(df, epochs, selection):

        # eyesstream video framerate is 49.7, epochs are recorded at 500 Hz
        eye_fr = 49.78
        freq = 500
        mult = eye_fr/freq

        selection = str(selection)
        # df['seconds'] = np.arange(0,len(df)/eye_fr,1/eye_fr)

        blinks = blink_isolation(df) 

        # blinks.to_csv("blink_if.csv")   
        
        fig = go.Figure(
            data=go.Scatter(
                # x=df['seconds'][round(epochs[selection][0]*mult):round(epochs[selection][1]*mult)], 
                # y=df['EAR_Avg'][round(epochs[selection][0]*mult):round(epochs[selection][1]*mult)],
                x = df['TS_corrected'][round(epochs[selection][0]*mult):round(epochs[selection][1]*mult)],
                y = df['EAR_Avg'][round(epochs[selection][0]*mult):round(epochs[selection][1]*mult)],
                name="EAR value",
                showlegend=False
            ),
        )

        fig.add_trace(
            go.Scatter(
                x=blinks['TS_corrected'][(blinks['Ind'] > round(epochs[selection][0]*mult)) & (blinks['Ind'] < round(epochs[selection][1]*mult))],
                y=blinks['EAR_Avg'][(blinks['Ind'] > round(epochs[selection][0]*mult)) & (blinks['Ind'] < round(epochs[selection][1]*mult))],
                mode="markers",
                name="Blinks",
                showlegend=False
            )
        )
        fig.update_layout(
            title=f"Blinks for Epoch {selection}",
            title_x=0.5,
            xaxis_title="Time (sec)",
            yaxis_title="EAR value",
            plot_bgcolor='rgb(11,82,91)',
            paper_bgcolor='rgb(27,58,75)',
            font_color="white"
        )
        return fig


    def interactive_dashboard():
        # df1 = pd.read_csv('./assets/data/sampleDataBM.csv')  # dummy data for now
        # df1 = df1.dropna()

        # define input vhdr filename
        root = '2022_01_14_T05_U002'
        vhdr_fname = './static/' + root + '/' + root + '_EEG01.vhdr'
        # define input vhdr filename
        var_name = 'HR'
        # define number of bins
        num_bins = 20
        # perform data processing: get data dictionary from raw data
        epochbm_dict, epochs = dp.data_processing(vhdr_fname, var_name, num_bins)
        # get slider with epochs
        slider = cs.create_slider(epochbm_dict)

        # Filepath of nii file from assets folder in the same directory
        img_file = "assets/BraTS19_2013_10_1_flair.nii"  # read in nii file from assets folder in same directory
        # Get the file of the cartesian coordinates
        filepath_name = 'assets/EEG01_chanlocs_cartesian.txt'

        # get visual parts
        data_brain, df = b3.brain_visual3(img_file, filepath_name)
        df = ef.findRegion(df)
        # print(data_brain)
        # df.to_csv("brain_df.csv")

        # get blinks detected
        video_path = './static/' + root + '/eyesstream.mp4'
        if not os.path.isfile(video_path):
            print("Eyestream path DNE or incorrect path. Blink detection module will be empty.")
        # blink_df = bd.eyestream_video_to_df(video_path)
        # raw_blink_df = pd.read_csv('./static/' + root + '/blinks.csv')
        # blink_df = blink_preprocess(raw_blink_df)

        # get audio scripts
        audio_path = './static/' + root + '/tobiiaudio.wav'
        epoch_scripts_cp = aud.audio_to_text(epochs, audio_path)
        epoch_scripts = epoch_scripts_cp
        epoch_objs = objs.obj_detect(epochs)
        print("Epoch scripts created")


        # external stylesheet for format
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        # main application
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        app.layout = html.Div(children=[
            html.Div([
                html.H1(
                    children=f"interactiveADELE - Trial: {'_'.join(map(str,vhdr_fname.split('/')[3].split('_')[:4]))}, epochs based on {var_name}",
                    style={
                        'textAlign': 'center'})
            ]),
            html.Div([
                slider,
                ], style={
                    'font-size': '12px',
                    'font-color': 'blue',
                    'padding': '10px'
            }),
            html.Div([  # upper row with brain and hr plot
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3(
                            children="Video Streams: POV and Eye view",
                            style={
                                'textAlign': 'center'
                            }
                        ),
                        dash_player.DashPlayer(
                            id='fullstream',
                            url='/static/' + root + '/fullstream.mp4',
                            controls=True,
                            width='650px',
                            height='450px',
                            style={'display': 'inline-block', 'margin-left': 100}
                        ),
                        dash_player.DashPlayer(
                            id='eyestream',
                            url = '/static/' + root + '/eyesstream.mp4',
                            controls=True,
                            width='113px',
                            height='450px',
                            style={'display': 'none'}
                        ),
                        html.Button(
                            'Play/Pause',
                            id='play-button',
                            n_clicks=1,
                            style={'display': 'inline-block', 'margin-left': 400, 'background-color': 'white'}
                        ),
                    ])
                    ]),
                ], className='six columns'),
                html.Div([
                    html.H3(
                        children="Graphs of biometrics - HR (Heart Rate)",
                        style={
                            # 'textAlign': 'center'
                            'margin-left': 100,
                        }
                    ),
                    dcc.Graph(id='hr-graph1',
                        style={
                            'display': 'inline-block'
                        })
                ], className='six columns'),
            ], className='row'),

            html.Div([  # second row
                html.Div([
                    html.Div([
                        html.H3(
                            children="3D interactive brain - alpha band",
                            style={
                                'textAlign': 'center',
                                # 'margin-left': 100
                            }
                        ),
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
                    html.H3(
                            children="3D interactive brain - theta band",
                            style={
                                'textAlign': 'center',
                                'margin-left': 100
                            }
                        ),
                        dcc.Graph(
                            id="image-display-graph-3d-1",
                            config=dict(displayModeBar=False),
                            style={
                                # 'margin-left': 100,
                                'display': 'inline-block',
                                'background-color': 'rgb(27,58,75)'
                                
                            })
                    # html.H3(
                    #     children="Graphs of biometrics - SpO2 (Blood Oxygen level)",
                    #     style={
                    #         # 'textAlign': 'center'
                    #         'margin-left': 50,
                    #     }
                    # ),
                    # dcc.Graph(id='SpO2-graph1',
                    #     style={
                    #         'display': 'inline-block'
                    #     })
                ], className='six columns')
            ], className='row'),

            # html.Div([  # third row
            #     html.Div([
            #         # html.Div([
            #         #     html.H3(
            #         #     children="Video Streams: POV and Eye view",
            #         #     style={
            #         #         'textAlign': 'center'
            #         #     }
            #         # ),
            #         #     dash_player.DashPlayer(
            #         #         id='fullstream',
            #         #         url='/static/' + root + '/fullstream.mp4',
            #         #         controls=True,
            #         #         width='650px',
            #         #         height='450px',
            #         #         style={'display': 'inline-block', 'margin-left': 100}
            #         #     ),
            #         #     dash_player.DashPlayer(
            #         #         id='eyestream',
            #         #         url = '/static/' + root + '/eyesstream.mp4',
            #         #         controls=True,
            #         #         width='113px',
            #         #         height='450px',
            #         #         style={'display': 'inline-block'}
            #         #     ),
            #         #     html.Button(
            #         #         'Play/Pause',
            #         #         id='play-button',
            #         #         n_clicks=1,
            #         #         style={'display': 'inline-block', 'margin-left': 425, 'background-color': 'white'}
            #         #     ),
            #         # ])
            #     ], className='six columns'),
            #     html.Div([
            #         html.H3(
            #             children="Blink Detection",
            #             style={
            #                 # 'textAlign': 'center'
            #                 'margin-left': 250,
            #             }
            #         ),
            #         dcc.Graph(id='blink-graph',
            #             style={
            #                 'display': 'inline-block'
            #             })
            #     ], className='six columns')
            # ], className='row'),

            html.Div([ # fourth row
                html.Div([
                    html.Div([
                        html.H3(
                        children="Object Detection on POV",
                        style={
                            'textAlign': 'center'
                        }
                    ),
                        dcc.Textarea(
                            id='objs_detected',
                            value=" ",
                            style={'display': 'inline-block', 'width': 800, 'height': 360, 'margin-left': 100, 'background-color': 'rgb(27,58,75)', 'color': 'white'}
                        )
                    ])
                ], className='six columns'),
                html.Div([
                    html.H3(
                        children="Audio Transcribing and Sentiment Analysis",
                        style={
                            # 'textAlign': 'center'
                            'margin-left': 100,
                        }
                    ),
                    dcc.Textarea(
                        id='text',
                        value=" ",
                        style={'display': 'inline-block', 'width': 700, 'height': 360, 'background-color': 'rgb(27,58,75)', 'color': 'white'}
                    )
                ], className='six columns')
            ], className='row')

        ],style={'backgroundColor': 'rgb(0,100,102)', 'color': 'white'})

        # Updates 3d brain 1 (Theta band) with the electrode to plot when slider is changed
        @app.callback(
            Output('image-display-graph-3d-1', 'figure'),
            [Input(slider.id, 'value')]  # for the electrode value
        )
        def update_graph(selected_value):
            high3 = he.highest_electrodes(epochbm_dict, selected_value, "Theta")
            fig = b3.make_3d_fig(data_brain, df, high3, "Theta")
            return fig

        # Updates 3d brain 2 (Alpha band) with the electrode to plot when slider is changed
        @app.callback(
            Output('image-display-graph-3d-2', 'figure'),
            [Input(slider.id, 'value')]  # for the electrode value
        )
        def update_graph(selected_value):
            high3 = he.highest_electrodes(epochbm_dict, selected_value, "Alpha")
            fig = b3.make_3d_fig(data_brain, df, high3, "Alpha")
            return fig

        # Updates hr plot when the slider is changed
        @app.callback(
            Output('hr-graph1', 'figure'),
            [Input(slider.id, 'value')]
        )
        def update_graph1(selected_value):
            fig = graph_biometric_selection('HR', epochbm_dict, selected_value)
            return fig

        # Updates SpO2 plot when the slider is changed
        # @app.callback(
        #     Output('SpO2-graph1', 'figure'),
        #     [Input(slider.id, 'value')]
        # )
        # def update_graph1(selected_value):
        #     fig = graph_biometric_selection('SpO2', epochbm_dict, selected_value)
        #     return fig

                # update blinks/EAR values for each epoch
        # @app.callback(
        #     Output('blink-graph', 'figure'),
        #     [Input(slider.id, 'value')]
        # )
        # def update_blink_graph(selected_value):
        #     fig = graph_blinks(blink_df,epochs,selected_value)
        #     return fig

        # Update video to start at Epoch start
        @app.callback(
            Output('fullstream', 'seekTo'),
            # Output('eyestream', 'seekTo'),
            Input(slider.id, 'value'),
            # Input('blink-graph', 'clickData'),
            Input('hr-graph1', 'clickData')
        )
        def update_video(value, clkData_hr):

            ctx = dash.callback_context
                        
            # print("States: ", ctx.states)
            # print("Inputs: ", ctx.inputs)
            # print("Triggered: ", ctx.triggered)  

            if not value:
                raise PreventUpdate
            else:
                if ctx.triggered[0]['prop_id'] == "Epoch Slider.value":
                    return (epochbm_dict[str(value)][0][0])/500
                # elif ctx.triggered[0]['prop_id'] == "blink-graph.clickData":
                #     return round(clkData_blink['points'][0]['x'],1), round(clkData_blink['points'][0]['x'],2)
                elif ctx.triggered[0]['prop_id'] == "hr-graph1.clickData":
                    return round(clkData_hr['points'][0]['x'],1)

        @app.callback(
            Output('fullstream', 'playing'),
            # Output('eyestream', 'playing'),
            Input('play-button', 'n_clicks')
        )
        def playpause_video(n_clicks):
            if n_clicks % 2 == 1:
                return False
            elif n_clicks % 2 == 0:
                return True

        # update objects detected for each epoch
        @app.callback(
            Output('objs_detected', 'value'),
            [Input(slider.id, 'value')]
        )
        def update_detects(value):
            return str('\n'.join(str(v) for v in epoch_objs[value-1]))

        # update transcript for each epoch
        @app.callback(
        Output('text','value'),
        [Input(slider.id, 'value')]
        )
        def update_text(value):
            return str('\n'.join(str(v) for v in epoch_scripts[value-1]))
            # return str(epoch_scripts[value-1])

        print("audio check 1")
        app.run_server(debug=True)
        print("audio check 2")

    interactive_dashboard()
