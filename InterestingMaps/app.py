
from xml.etree.ElementTree import tostring
from dash import Dash, html, dash_table, dcc, callback, Input, Output, State
import json
import math
from plotly import io as pio
import plotly.express as px
import os
import numpy as np
import pandas as pd
from plotly.graph_objs import layout


with open('countries.json', encoding='utf8') as file:
    countries = json.load(file)



df = pd.read_csv("GDPFile.csv")
df.rename(columns={'Country Code': 'adm0_a3'}, inplace=True)
selected_vals = pd.json_normalize(countries['features'], max_level=5)
selected_vals = selected_vals['properties.adm0_a3']
mask = df['adm0_a3'].isin(selected_vals)
df = df[mask]




#APP CODE
app = Dash(__name__)
app.layout = html.Div([
    html.H1("Per capita GDP map by year", style={'textAlign': 'center'}),
    html.Div([
        dcc.Graph(id='map-box', figure=px.choropleth_mapbox(df, geojson=countries, featureidkey="properties.adm0_a3", locations='adm0_a3', color='2022',
                           color_continuous_scale="Viridis",
                           mapbox_style="carto-positron",
                           hover_name = "Country Name",
                           #hover_data = ['2022'],
                           range_color=(0, 120000),
                           #scope="world",
                           zoom=0,
                           labels={'2022':'GDP per capita (USD)'},
                           height=600,
                           width=900
         )),
    ],style={"display": "flex", "justifyContent": "center"},
    ),                      
    html.Div([
        dcc.Slider(1967, 2022, 1,
                value=2022,
                id='year-slider',
                    marks={i: f"{i}" for i in range(1970,2021, 10)},
            )
        ],style={"width" : "70%","padding-left":"15%", "padding-right":"15%"})
    #dash_table.DataTable(data=df.to_dict('records'), page_size=10)
    ])

@callback(Output('map-box', 'figure'), Input('year-slider', 'value'), State('map-box', 'relayoutData'))
def update_output(value, state):
    label  = str(value)    
       
    zm = 0
    cent = {}
    pch = 0
    bear = 0
    if state is not None:
        if "mapbox.zoom" in state.keys():
            zm = state['mapbox.zoom']
        if "mapbox.center" in state.keys():
            cent = state['mapbox.center']
        if "mapbox.bearing" in state.keys():
            bear = state['mapbox.bearing']
        if "mapbox.pitch" in state.keys():
            pch = state['mapbox.pitch']

    max_val = 0.8*np.max(df[label])
    max_val /= 10000
    max_val = 10000*math.ceil(max_val)

    figure = px.choropleth_mapbox(df, geojson=countries, featureidkey="properties.adm0_a3", locations='adm0_a3', color=label,
                           color_continuous_scale="Viridis",
                           mapbox_style="white-bg",
                           range_color=(0, max_val),
                           labels={label:'GDP per capita (USD)'},
                           hover_name = "Country Name",
                           hover_data = {label:True, 'adm0_a3':False},
                           zoom=zm,
                           center=cent,
                           height=600,
                           width=900
                           )
    figure.update_mapboxes(pitch=pch, bearing=bear)
    #figure.update_layout(mapbox_style="white-bg")
    #figure.update_layout(mapbox_bounds={"west":-180, "east":180, "north":90,"south":-90})
    return figure

if __name__ == '__main__':
    app.run(debug=True)