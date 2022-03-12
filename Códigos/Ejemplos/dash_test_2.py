from dataclasses import dataclass
from os import stat
#from readline import get_history_item
from turtle import color, end_fill
#from cv2 import line
import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
#from iexfinance.stocks import get_historical_data
import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import date
from datetime import datetime
import time

#Día actual
today = date.today()


#FASE 1: Obtención de los Datos

FechaIni="2021-01-01"
FechaFin=today

app= dash.Dash(__name__)

app.layout=html.Div([

html.H1(children="DASHBOARD TEST 1"),
html.Label("DASH GRAPH"),

html.Div([
dcc.Input(
    id="stock_input",
    placeholder="Enter a stock to be charter",
    type="text",
    value="AMZN"
)]),

html.Div(
    [
        html.H2("Stock App"),
        html.Img(src="/assets/grafico.png")

    ], className="banner"
),

html.Div(
    [
        html.Div([
            dcc.Graph(
                id="graph_close",
            )
        ], className="six columns"),

    ], className="row"
)
,

html.Div(dcc.Dropdown(
    options=[
        {'label':"Candlestick","value":"Candlestick"},
        {"label":"Line","value":"Line"}
    ]
))

])

#pp.css.append_css({"external_url":"https://codepen.io/chriddyp/pen/bWLwgP.css"})

@app.callback(Output("graph_close","figure"),
            [Input("stock_input","value")]
            )


def update_fig(input_value):
    time.sleep(2)
    df=yf.download(input_value,FechaIni,FechaFin)

    data=[]

    trace_close=go.Scatter(x=list(df.index),
                       y=list(df.Close),
                       name="Close",
                       line=dict(color="#f44242"))


    data.append(trace_close)

    layout={"title":"Callback Graph"}

    print(df.info())

    return {"data":data,
            "layout":layout
            }

if __name__=="__main__":
    app.run_server(debug=True)