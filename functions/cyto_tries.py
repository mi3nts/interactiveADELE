import dash
import dash_cytoscape as cyto
# import dash_html_components as html
from dash import html
import pandas as pd
import matplotlib.pyplot as plt
from dash import dcc
from dash.dependencies import Input, Output
from itertools import chain
from itertools import combinations

app = dash.Dash(__name__)

df = pd.read_csv("assets\EEG01_chanlocs_cartesian.txt", delim_whitespace=True, names=['Name', 'x', 'y', 'z'])
# print(df.shape)
# df.columns = ["Electrode","x","y","z"]

# plt.scatter(df['x'],df['y'])
# plt.show()


# print(df["x"])

full_list = {'Alpha': [['TP7', 'FT9', 'FT7'], ['F8', 'Fp2', 'Fp1'], ['Fp2', 'PO7', 'Fpz'], ['F8', 'Fp2', 'Fp1'], ['P6', 'P8', 'P4'], ['F8', 'P6', 'P8'], ['F8', 'P6', 'FT9'], ['Fp1', 'P6', 'AF7'], ['F8', 'Fp1', 'FC3'], ['TP7', 'PO7', 'P6']], 'Beta': [['PO7', 'TP7', 'T8'], ['T8', 'C6', 'PO7'], ['T8', 'TP7', 'C6'], ['F8', 'PO7', 'T8'], ['T8', 'C6', 'PO7'], ['T8', 'C6', 'PO7'], ['T8', 'C6', 'F8'], ['T8', 'C6', 'PO7'], ['T8', 'C6', 'PO7'], ['PO7', 'T8', 'C6']]}

alpha_edges_all = []
for epoch in full_list['Alpha']:
    alpha_edges_all.extend(list(combinations(epoch,2)))

nodes = [
    {
        'data': {'id': short, 'label': short},
        'position': {'x': x, 'y': y}
    }
    for short, short, y, x in (
        list(zip(df["Name"],df["Name"],-df["x"],-df["y"]))

    )
]

edges = [
    {'data': {'source': source, 'target': target}}
    for source, target in(
        alpha_edges_all
    )
]

# edges = [
#     {'data': {'source': source, 'target': target}}
#     for source, target in (
#         ('van', 'la'),
#         ('la', 'chi'),
#         ('hou', 'chi'),
#         ('to', 'mtl'),
#         ('mtl', 'bos'),
#         ('nyc', 'bos'),
#         ('to', 'hou'),
#         ('to', 'nyc'),
#         ('la', 'nyc'),
#         ('nyc', 'bos')
#     )
# ]
default_stylesheet = [
    {
        "selector": "node",
        "style": {
            "width": "10px",
            "height": "10px",
            "content": "data(label)",
            "font-size": "4px",
            "text-valign": "center",
            "text-halign": "center",
        }  
    },
]
elements = nodes + edges
# + edges

app.layout = html.Div([
    dcc.Slider(
        min=1,
        max=10,
        step=1,
        value=1,
        id='slider',  
    ),
    cyto.Cytoscape(
        id='cytoscape-layout-1',
        elements=elements,
        style={'width': '100%', 'height': '700px'},
        layout={
            'name': 'preset'
        },
        stylesheet=default_stylesheet
    )
])

@app.callback(
    Output('cytoscape-layout-1', 'stylesheet'),
    Input('slider', 'value')
)
def update_alpha_network(value):
    hl_nodes = full_list['Alpha'][value]
    # print(hl_nodes)

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
        {"selector": "edge",
            "style": {
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
                        'background-color': 'blue',
                        'z-index': 9999
                    }
        })

    alpha_nodes = list(set(chain(*full_list['Alpha'])))

    for i in alpha_nodes:
        if i not in hl_nodes:
            stylesheet.append({
                'selector': f'[label = "{i}"]',
                    'style':
                        {'opacity': 0.3,
                         'background-color': node_border_color_alpha}
                }
            )

    return stylesheet

if __name__ == '__main__':
    app.run_server(debug=True, port=8090)