from dataclasses import dataclass
from os import stat
from readline import get_history_item
from turtle import color, end_fill
from cv2 import line
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from iexfinance.stocks import get_historical_data
import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go


#FASE 1: Obtención de los Datos

Activo="COP=X"
FechaIni="2019-01-01"
FechaFin="2022-03-03"


df=yf.download(Activo,FechaIni,FechaFin)
print(df.info())

trace_close=go.Scatter(x=list(df.index),
                       y=list(df.Close),
                       name="Close",
                       line=dict(color="#f44242"))

data=[trace_close]
layout=dict(title=Activo,
       showlegend=False)

fig = dict(data=data, layout=layout)


app= dash.Dash(__name__)

app.layout=html.Div([

html.Div(
    [
        html.H2("Stock App"),
        html.Img(src="/assets/grafico.png")

    ], className="banner"
),

html.H1(children="DASHBOARD TEST"),
html.Label("DASH GRAPH"),
html.Div(
dcc.Input(
    id="Stock-input",
    placeholder="Enter a stock to be charter",
    type="text",
    value=""
)
),

html.Div(dcc.Dropdown(
    options=[
        {'label':"Candlestick","value":"Candlestick"},
        {"label":"Line","value":"Line"}
    ]
)),

html.Div(
    dcc.Graph(id="Stock Chart",
              figure=fig)
    )
])


"""app.css.append_css(
    {
        "external_url":"https://"
    }
)"""

if __name__=="__main__":
    app.run_server(debug=True)