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
from matplotlib.pyplot import text
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
import network_display as nd
import dash_player
from dash.dependencies import Input, Output
import numpy as np
from sklearn.ensemble import IsolationForest
from dash.exceptions import PreventUpdate
import itertools
import dash_cytoscape as cyto
import more_itertools as mit

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
            font_color="white",
            width=600
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

        # print(count)
        # print("Blinks count: " + count)

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

        blinks= blink_isolation(df)

        blinks_list_iso = [list(group) for group in mit.consecutive_groups(blinks.index)]

        count = 0
        blinks_iso_grouped = []

        for i in blinks_list_iso:
            if len(i) > 2:
                blinks_iso_grouped.append(i)
                count += 1
        tot_blinks = round((count/(len(df)/eye_fr))*60,2)
        # print(blink_count)

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
        # print(blinks['TS_corrected'][(blinks['Ind'] > round(epochs[selection][0]*mult)) & (blinks['Ind'] < round(epochs[selection][1]*mult))])
        # print(blinks['TS_corrected'][(blinks['Ind'] > round(epochs[selection][0]*mult)) & (blinks['Ind'] < round(epochs[selection][1]*mult))].shape)
        smth = blinks['TS_corrected'][(blinks['Ind'] > round(epochs[selection][0]*mult)) & (blinks['Ind'] < round(epochs[selection][1]*mult))]


        fig.update_layout(
            title=f"Blinks for Epoch {selection}",
            title_x=0.5,
            xaxis_title="Time (sec)",
            yaxis_title="EAR value",
            plot_bgcolor='rgb(11,82,91)',
            paper_bgcolor='rgb(27,58,75)',
            font_color="white"
        )
        return fig, smth, tot_blinks


    def interactive_dashboard():
        # df1 = pd.read_csv('./assets/data/sampleDataBM.csv')  # dummy data for now
        # df1 = df1.dropna()

        # define input vhdr filename
        root = '2020_06_04_T09_U00T'
        vhdr_fname = './static/' + root + '/' + root + '_EEG01.vhdr'
        # define input vhdr filename
        var_name = 'HR'
        # define number of bins
        num_bins = 10
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

        # get nodes and edges for network
        band_list = ["Alpha","Beta"]
        threeElecFullDict = {key: None for key in band_list}
        for j in band_list:
            dummy_list = []
            for i in range(1,num_bins+1):
                dummy_df = list(epochbm_dict[str(i)][1][j].sort_values(ascending=False).iloc[0:3:].index.values)
                dummy_list.append(dummy_df)
            # print(j)
            threeElecFullDict[j] = dummy_list
            # threeElecListFull = he.highest_electrodes(epochbm_dict, selected_value, "Alpha",num_bins)[1]
        # print(threeElecFullDict)
        nodes, alpha_edges = nd.nodesEdges(threeElecFullDict['Alpha'])
        nodes, beta_edges = nd.nodesEdges(threeElecFullDict['Beta'])
        alpha_elems = nodes + alpha_edges
        beta_elems = nodes + beta_edges
        # elems = nodes + edges

        # get blinks detected
        video_path = './static/' + root + '/eyesstream.mp4'
        # blink_df = bd.eyestream_video_to_df(video_path)
        raw_blink_df = pd.read_csv('./static/' + root + '/blinks.csv')
        blink_df = blink_preprocess(raw_blink_df)

        # get audio scripts
        # audio_path = './static/' + root + '/tobiiaudio.wav'
        # epoch_scripts_cp = aud.audio_to_text(epochs, audio_path)
        # epoch_scripts = epoch_scripts_cp
        # epoch_objs = objs.obj_detect(epochs)
        # print("Epoch scripts created")


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
                        html.H3(
                            children="3D interactive brain - theta band ~ 4-8 Hz",
                            style={
                                'textAlign': 'center'
                            }
                        ),
                        dcc.Graph(
                            id="image-display-graph-3d-1",
                            config=dict(displayModeBar=False),
                            style={
                                'margin-left': 10,
                                'display': 'inline-block',
                                'background-color': 'rgb(27,58,75)'
                                
                            })
                    ]),
                ], className='six columns'),
                html.Div([
                    ###
                    html.H3(
                        children="Network of High Activity Electrodes (Alpha band ~ 8-12 Hz)",
                        style={
                            # 'textAlign': 'center'
                            'margin-left': 100,
                        }
                    ),
                    cyto.Cytoscape(
                        id='alpha-network',
                        layout={'name': 'preset'},
                        elements=alpha_elems,
                        stylesheet=nd.genStylesheet(),
                        style={
                            'width': '450px', 
                            'height': '450px',
                            'display': 'inline-block'}
                    ),
                    cyto.Cytoscape(
                        id='beta-network',
                        layout={'name': 'preset'},
                        elements=beta_elems,
                        stylesheet=nd.genStylesheet(),
                        style={
                            'width': '450px', 
                            'height': '450px',
                            'display': 'inline-block'}
                    ),
                    # htm
                    # html.P(id='cytoscape-mouseoverNodeData-output'),
                    ###
                ], className='six columns'),
            ], className='row'),

            html.Div([  # second row
                html.Div([
                    html.H3(
                        children="Report",
                        style={'margin-left': 100}
                    
                    ),
                    dcc.Textarea(
                        id="report-text",
                        value="",
                        style={'display': 'inline-block', 'width': 700, 'height': 360,  'background-color': 'rgb(27,58,75)', 'color': 'white'}
                    )

                ], className='six columns'),
                # html.Div([
                #     html.Div([
                #         html.H3(
                #             children="3D interactive brain - alpha band",
                #             style={
                #                 'textAlign': 'center'
                #                 # 'margin-left': 200,
                #             }
                #         ),
                #         dcc.Graph(
                #             id="image-display-graph-3d-2",
                #             config=dict(displayModeBar=False),
                #             style={
                #                 'margin-left': 10,
                #                 'display': 'inline-block'}
                #         )
                #     ])
                # ], className='six columns'),
                html.Div([
                    ###
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
                    ###

                ], className='six columns')
            ], className='row'),

            html.Div([  # third row
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
                            # url='/static/' + root + '/fullstream.mp4',
                            url = '/static/' + root + '/conv_detected.mp4',
                            controls=True,
                            width='550px',
                            height='450px',
                            style={'display': 'inline-block', 'margin-left': 10}
                        ),
                        dash_player.DashPlayer(
                            id='eyestream',
                            url = '/static/' + root + '/eyesstream.mp4',
                            controls=True,
                            width='90px',
                            height='450px',
                            style={'display': 'inline-block'}
                        ),
                        html.Button(
                            'Play/Pause',
                            id='play-button',
                            n_clicks=1,
                            style={'display': 'inline-block', 'margin-left': 350, 'background-color': 'white'}
                        ),
                    ])
                ], className='six columns'),
                html.Div([
                    html.H3(
                        children="Blink Detection",
                        style={
                            # 'textAlign': 'center'
                            'margin-left': 275,
                        }
                    ),
                    dcc.Graph(id='blink-graph',
                        style={
                            'display': 'inline-block'
                        })
                ], className='six columns')
            ], className='row'),

            # html.Div([ # fourth row
            #     html.Div([
            #         html.Div([
            #             html.H3(
            #             children="Object Detection on POV",
            #             style={
            #                 'textAlign': 'center'
            #             }
            #         ),
            #             dcc.Textarea(
            #                 id='objs_detected',
            #                 value=" ",
            #                 style={'display': 'inline-block', 'width': 800, 'height': 360, 'margin-left': 100, 'background-color': 'rgb(27,58,75)', 'color': 'white'}
            #             )
            #         ])
            #     ], className='six columns'),
            #     html.Div([
            #         html.H3(
            #             children="Audio Transcribing and Sentiment Analysis",
            #             style={
            #                 # 'textAlign': 'center'
            #                 'margin-left': 100,
            #             }
            #         ),
            #         dcc.Textarea(
            #             id='text',
            #             value=" ",
            #             style={'display': 'inline-block', 'width': 700, 'height': 360, 'background-color': 'rgb(27,58,75)', 'color': 'white'}
            #         )
            #     ], className='six columns')
            # ], className='row')

        ],style={'backgroundColor': 'rgb(0,100,102)', 'color': 'white'})

        # Updates 3d brain 1 (Theta band) with the electrode to plot when slider is changed
        @app.callback(
            Output('image-display-graph-3d-1', 'figure'),
            [Input(slider.id, 'value')]  # for the electrode value
        )
        def update_graph(selected_value):
            high3 = he.highest_electrodes(epochbm_dict, selected_value, "Theta",num_bins)[0]
            fig = b3.make_3d_fig(data_brain, df, high3, "Theta")
            return fig

        # Updates hr plot when the slider is changed
        @app.callback(
            Output('hr-graph1', 'figure'),
            [Input(slider.id, 'value')]
        )
        def update_graph1(selected_value):
            fig = graph_biometric_selection('HR', epochbm_dict, selected_value)
            return fig

        # Update alpha network display
        @app.callback(
            Output('alpha-network', 'stylesheet'),
            Input(slider.id, 'value')
        )
        def update_alpha_network(value):
            hl_nodes = threeElecFullDict['Alpha'][value-1]

            node_text_color = 'blue'
            node_color = 'blue'
            node_size = '15px'
            node_text_size = '5px'
            node_border_color_alpha = 'blue'

            stylesheet = [
                {'selector': 'node',
                 'style': 
                    {'label': 'data(label)',
                     'width': node_size,
                     'height': node_size,
                     "text-valign": "center",
                     "text-halign": "center",
                     "font-size": "5px",
                     'shape':'circle'}
                },
                {'selector': 'edge',
                    'style': {
                        'opacity': 0.2,
                        'width': 1,
                        'line-color': node_color
                    }
                }
            ]
            for i in hl_nodes:
                stylesheet.append({
                    'selector': f'[label = "{i}"]',
                        'style':
                            {
                                'background-color': node_color,
                                'z-index': 9999
                            }
                })

            all_alpha_nodes = list(set(itertools.chain(*threeElecFullDict['Alpha'])))

            for i in all_alpha_nodes:
                if i not in hl_nodes:
                    stylesheet.append({
                        'selector': f'[label = "{i}"]',
                            'style':
                                {'opacity': 0.3,
                                'background-color': node_border_color_alpha}
                        }
                    )
            return stylesheet

        # Update beta network display
        @app.callback(
            Output('beta-network', 'stylesheet'),
            Input(slider.id, 'value')
        )
        def update_beta_network(value):
            hl_nodes = threeElecFullDict['Beta'][value-1]

            node_text_color = 'purple'
            node_color = 'purple'
            node_size = '15px'
            node_text_size = '5px'
            node_border_color_alpha = 'purple'

            stylesheet = [
                {'selector': 'node',
                 'style': 
                    {'label': 'data(label)',
                     'width': node_size,
                     'height': node_size,
                     "text-valign": "center",
                     "text-halign": "center",
                     "font-size": "5px",
                     'shape':'circle'}
                },
                {'selector': 'edge',
                    'style': {
                        'opacity': 0.2,
                        'width': 1,
                        'line-color': node_color
                    }
                }
            ]
            for i in hl_nodes:
                stylesheet.append({
                    'selector': f'[label = "{i}"]',
                        'style':
                            {
                                'background-color': node_color,
                                'z-index': 9999
                            }
                })

            all_beta_nodes = list(set(itertools.chain(*threeElecFullDict['Beta'])))

            for i in all_beta_nodes:
                if i not in hl_nodes:
                    stylesheet.append({
                        'selector': f'[label = "{i}"]',
                            'style':
                                {'opacity': 0.3,
                                'background-color': node_border_color_alpha}
                        }
                    )
            return stylesheet

        @app.callback(
            Output('report-text','value'),
            Output('blink-graph','figure'),
            Input(slider.id, 'value')
        )
        def epoch_details(epoch):
            # print(epoch)
            # epoch start, epoch end, length, average HR           
            fig,data,total_blinks = graph_blinks(blink_df,epochs,epoch)

            blinks_list_iso = [list(group) for group in mit.consecutive_groups(data.index)]

            # counts the number of blinks and where they occur, given there are consecutive records (i.e. duration of the predicted blink) 
            # is longer than metric specified by dur
            count = 0
            blinks_iso_grouped = []
    
            for i in blinks_list_iso:
                if len(i) > 2:
                    blinks_iso_grouped.append(i)
                    count += 1
            
            time_start = epochs[str(epoch)][0]/500
            time_end = epochs[str(epoch)][1]/500

            blinks_report = "Blinks in epoch: " + str(round(count,2)) + ", " + str(round((count/(time_end-time_start))*60,2)) + " blinks per minute. \n" + \
                "Blinks per minute for full event: " + str(total_blinks)

            # y_df = epochbm_dict[epoch][2][biometric]
            hr  = "Epoch " + str(epoch) + " from " + str(round(time_start,2)) + "s to " + str(round(time_end,2)) + " s. Average HR for epoch: " + \
                str(round(epochbm_dict[str(epoch)][2]['HR'].mean(),2)) + "\n"

            hl_nodes = threeElecFullDict['Alpha'][epoch-1]
            # print(hl_nodes)
            
            ha_elecs = "The following are the high activity electrodes in the alpha band: " + str(hl_nodes[0]) + ", " + str(hl_nodes[1]) + ", " + str(hl_nodes[2]) + ". \n" + \
                str(hl_nodes[0]) + " maps to brodmann area " + str(ef.elec2ba(hl_nodes[0])) + " and associated with " + str(ef.elec2area(hl_nodes[0])) + ". \n" + \
                str(hl_nodes[1]) + " maps to brodmann area " + str(ef.elec2ba(hl_nodes[1])) + " and associated with " + str(ef.elec2area(hl_nodes[1])) + ". \n" + \
                str(hl_nodes[2]) + " maps to brodmann area " + str(ef.elec2ba(hl_nodes[2])) + " and associated with " + str(ef.elec2area(hl_nodes[2])) + ". \n" 

            # print(blink_df)

            text_block = hr + "\n" + ha_elecs + "\n" + blinks_report
            # print(text_block)

            return text_block, fig

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
        #     Output('report-text', 'value'),
        #     [Input(slider.id, 'value')]
        # )
        # def update_blink_graph(selected_value):
            
            # print(data[5], type(data[5]))
            # print(data.index.to_list())

            # creates a list of lists that keeps track of groups of consecutive records


        # Update video to start at Epoch start
        @app.callback(
            Output('fullstream', 'seekTo'),
            Output('eyestream', 'seekTo'),
            Input(slider.id, 'value'),
            Input('blink-graph', 'clickData')
        )
        def update_video(value, clkData):

            ctx = dash.callback_context
                        
            # print("States: ", ctx.states)
            # print("Inputs: ", ctx.inputs)
            # print("Triggered: ", ctx.triggered)  

            if not value:
                raise PreventUpdate
            else:
                if ctx.triggered[0]['prop_id'] == "Epoch Slider.value":
                    return (epochbm_dict[str(value)][0][0])/500, (epochbm_dict[str(value)][0][0])/500
                elif ctx.triggered[0]['prop_id'] == "blink-graph.clickData":
                    return round(clkData['points'][0]['x'],1), round(clkData['points'][0]['x'],2)

        @app.callback(
            Output('fullstream', 'playing'),
            Output('eyestream', 'playing'),
            Input('play-button', 'n_clicks')
        )
        def playpause_video(n_clicks):
            if n_clicks % 2 == 1:
                return False, False
            elif n_clicks % 2 == 0:
                return True, True

        # update objects detected for each epoch
        # @app.callback(
        #     Output('objs_detected', 'value'),
        #     [Input(slider.id, 'value')]
        # )
        # def update_detects(value):
        #     return str('\n'.join(str(v) for v in epoch_objs[value-1]))

        # update transcript for each epoch
        # @app.callback(
        # Output('text','value'),
        # [Input(slider.id, 'value')]
        # )
        # def update_text(value):
        #     return str('\n'.join(str(v) for v in epoch_scripts[value-1]))
            # return str(epoch_scripts[value-1])
 
        app.run_server(debug=True)

    interactive_dashboard()
