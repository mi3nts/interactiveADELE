# CODE TO DISPLAY A 3D BRAIN MODEL WITH A SINGLE EEG ELECTRODE PLOT AND A SECONDARY COMPONENT

# CODE AUTHORED BY: MICHAEL LEE
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - data_brain_file - filename of the brain nii file
#   - coordinate_file - filename of the electrode cartesian coordinates
#   - callback_object1 - the secondary dash_core_component or dash_html_component
#   - property1 - the property of the secondary component which determines the plot point

# OUTPUTS
#   - app - Plotly Dash app with the 3d brain Graph and secondary component

# ADELE DEPENDENCIES
#   - none

# ADELE DEPENDERS
#   - none
# ==============================================================================

# import statements
import dash
from dash import html
from dash import dcc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from skimage import measure, img_as_ubyte
from nilearn import image


# Function taken from https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-3d-image-partitioning
def combine_last_dim(
        img,
        output_n_dims=3,
        combiner=lambda x: (np.sum(np.abs(x), axis=-1) != 0).astype("float"),
):
    if len(img.shape) == output_n_dims:
        return img
    imgout = combiner(img)
    return imgout


# Function taken from https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-3d-image-partitioning
# function that takes in brain nii array and returns Mesh data using the plotly 3d mesh
# input -  brain nii array
# output - brain data array
def create_brain_data(img):
    # image, color
    images = [
        (img.transpose((1, 2, 0))[:, :, ::-1], "grey"),
    ]

    data_brain = []

    for im, color in images:
        im = combine_last_dim(im)
        try:
            verts, faces, normals, values = measure.marching_cubes(im, 0, step_size=3)
            x, y, z = verts.T
            i, j, k = faces.T
            data_brain.append(
                go.Mesh3d(x=x, y=y, z=z, color=color, opacity=0.2, i=i, j=j, k=k)
            )
        except RuntimeError:
            continue

    return data_brain


# Function that creates the 3d brain figure using the brain data array
# input - the brain data array, the dataframe of all electrode locations, the name of the electrode to plot
# output - the figure with the 3d brain and single electrode plot
def make_3d_fig(data_brain, df, callback_value):
    # adapted from plotly dash
    # creates the default brain
    default_3d_layout = dict(
        scene=dict(
            yaxis=dict(visible=False, showticklabels=False, showgrid=False, ticks=""),
            xaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.25, y=1.25, z=1.25),
            ),
        ),
        height=800,
    )

    fig = go.Figure(data=data_brain)  # from plotly.graph objects module
    fig.update_layout(**default_3d_layout)

    # create the plot point
    fig2 = go.FigureWidget(fig)  # create widget to add components

    xoffset = 84.5385 + 35
    yoffset = 84.9812 + 45
    zoffset = 42.0882 + 25

    myrow = df.loc[df["Name"] == callback_value]
    if (myrow.empty):
        myrow = df.loc[df["Name"] == "Fp1"]

    myrowx = myrow.iloc[0]['x']
    myrowy = myrow.iloc[0]['y']
    myrowz = myrow.iloc[0]['z']

    fig2.add_scatter3d(x=[myrowy + xoffset],
                       y=[-myrowx + yoffset],
                       z=[myrowz + zoffset],
                       marker_size=[50, 50, 50],
                       marker=dict(color='green'),
                       name=myrow.iloc[0]['Name']
                       )

    return fig2


# Function that creates the app with the 3d brain Graph
# input -   data_brain_file = filename of the input nii file,
#           coordinate_file = filename of the electrode cartesian coordinates,
#           callback_object1 = the secondary component,
#           property1 = the property of the secondary component which determines the plot point
# output - the app containing the 3d graph and the callback object
def brain_visual(data_brain_file, coordinate_file, callback_object1, property1):
    # First 3 lines adapted from Github:
    # https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-3d-image-partitioning
    img = image.load_img(data_brain_file)
    img = img.get_fdata().transpose(2, 0, 1)[::-1].astype("float")
    img = img_as_ubyte((img - img.min()) / (img.max() - img.min()))

    # Create the default 3d brain
    data_brain = create_brain_data(img)

    # Get the file of the cartesian coordinates
    df = pd.read_csv(coordinate_file, delim_whitespace=True, names=['Name', 'x', 'y', 'z'])

    # Set up the app with the 3d brain and the secondary component
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Graph(
            id="image-display-graph-3d",
            config=dict(displayModeBar=False),
            # figure=fig
        ),
        callback_object1
    ])

    # Updates graph when callback_object1 is changed
    @app.callback(
        dash.dependencies.Output('image-display-graph-3d', 'figure'),
        dash.dependencies.Input(callback_object1.id, property1)
    )
    def update_graph(selected_value):
        fig = make_3d_fig(data_brain, df, selected_value)
        return fig

    return app


# Sample main function to run app
# if __name__ == "__main__":
#     # Filepath of nii file from assets folder in the same directory
#     img_file = "assets/BraTS19_2013_10_1_flair.nii"  # read in nii file from assets folder in same directory
#
#     # Get the file of the cartesian coordinates
#     filepath_name = 'assets/EEG01_chanlocs_cartesian.txt'
#
#     # Secondary component that determines what coordinate to plot
#     mydropdown = dcc.Dropdown(
#         id='dropdown1-for-graph',
#         options=[
#             {'label': 'Fp1', 'value': 'Fp1'},
#             {'label': 'Fp2', 'value': 'Fp2'},
#             {'label': 'F3', 'value': 'F3'},
#             {'label': 'F4', 'value': 'F4'},
#             {'label': 'C3', 'value': 'C3'}
#         ],
#         value='Fp1'
#     )
#
#     app = brain_visual(img_file, filepath_name, mydropdown, 'value')
#     app.run_server(debug=True)
