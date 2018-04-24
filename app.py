import os
import arrow
import requests
import functools
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.plotly as py
from flask import Flask, json
from dash import Dash
from dash.dependencies import Input, Output


py.sign_in(os.environ['PLOTLY_USERNAME'], os.environ['PLOTLY_API_KEY'])

usgs = 'http://earthquake.usgs.gov/earthquakes/'
geoJsonFeed = 'feed/v1.0/summary/4.5_month.geojson'
url = '{}{}'.format(usgs, geoJsonFeed)
req = requests.get(url)
data = json.loads(req.text)


mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN', 'mapbox-token')


theme = {
    'font-family': 'Raleway',
    'background-color': '#787878',
}


def convert_timestamp(timestamp_ms):
    return arrow.get(timestamp_ms / 1000.0).format()


def create_dataframe(d):
    features = d['features']
    properties = [x['properties'] for x in features]
    geometries = [x['geometry'] for x in features]
    coordinates = [x['coordinates'] for x in geometries]
    times = [convert_timestamp(x['time']) for x in properties]
    dd = {
        'Place': [x['place'] for x in properties],
        'Magnitude': [x['mag'] for x in properties],
        'Time': times,
        'Detail': [x['detail'] for x in properties],
        'Longitude': [x[0] for x in coordinates],
        'Latitude': [x[1] for x in coordinates],
        'Depth': [x[2] for x in coordinates],
    }
    # html text to display when hovering
    texts = list()
    for i in range(len(properties)):
        text = '{}<br>{}<br>Magnitude: {}<br>Depth: {} km'.format(
            dd['Time'][i], dd['Place'][i], dd['Magnitude'][i], dd['Depth'][i])
        texts.append(text)
    dd.update({'Text': texts})
    return pd.DataFrame(dd)


def create_metadata(d):
    dd = {
        'title': d['metadata']['title'],
        'api': d['metadata']['api'],
    }
    return dd

dataframe = create_dataframe(data)
metadata = create_metadata(data)
# print(dataframe.head())


def create_td(series, col):
    val = series[col]
    if col == 'Detail':
        td = html.Td(
            html.A(children='GeoJSON', href='{}'.format(val), target='_blank'))
    else:
        td = html.Td(val)
    return td


def create_table(df):
    columns = ['Magnitude', 'Latitude', 'Longitude', 'Time', 'Place', 'Detail']
    num_rows = data['metadata']['count']
    thead = html.Thead(html.Tr([html.Th(col) for col in columns]))
    table_rows = list()
    for i in range(num_rows):
        tr = html.Tr(
            children=list(map(functools.partial(create_td, df.iloc[i]),
                              columns)))
        table_rows.append(tr)
    tbody = html.Tbody(children=table_rows)
    table = html.Table(children=[thead, tbody], id='my-table')
    return table


def create_header(some_string):
    header_style = {
        'background-color': theme['background-color'],
        'padding': '1.5rem',
    }
    header = html.Header(html.H1(children=some_string, style=header_style))
    return header


app_name = 'Dash Earthquakes'
server = Flask(app_name)
server.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
app = Dash(name=app_name, server=server)

app.layout = html.Div(
    children=[
        create_header(app_name),
        html.Div(
            children=[
                html.Div(create_table(dataframe), className='row'),
            ],
        ),
    ],
    className='container',
    style={'font-family': theme['font-family']}
)


external_js = [
    # jQuery, DataTables, script to initialize DataTables
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    '//cdn.datatables.net/1.10.15/js/jquery.dataTables.min.js',
    'https://codepen.io/jackdbd/pen/bROVgV.js',
]

external_css = [
    # dash stylesheet
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css?family=Raleway',
    # 'https://fonts.googleapis.com/css?family=Lobster',
    '//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    '//cdn.datatables.net/1.10.15/css/jquery.dataTables.min.css',
]

for js in external_js:
    app.scripts.append_script({'external_url': js})

for css in external_css:
    app.css.append_css({'external_url': css})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=True,  port=port, threaded=True)
