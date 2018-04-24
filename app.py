import os
import datetime
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


def query_data():
    url = r"http://localhost:9200/dashboard/klocwork/_search?pretty"
    resp = requests.get(url)
    records = resp.json()["hits"]["hits"]
    records = map(lambda r: r["_source"], records)
    return list(records)


theme = {
    'font-family': 'Raleway',
    'background-color': '#787878',
}


def create_dataframe(d):
    return pd.DataFrame(d)

data = query_data()
dataframe = create_dataframe(data)


def create_td(series, col):
    val = series[col]
    if col == 'file_url_path':
        td = html.Td(
            html.A(children='url', href='{}'.format(val), target='_blank'))
    else:
        td = html.Td(val)
    return td


def create_table(df):
    columns = df.columns.tolist()
    num_rows = len(df)
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


app_name = 'klocwork Tables'
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
