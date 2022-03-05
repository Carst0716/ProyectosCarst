from dataclasses import dataclass
from os import stat
#from readline import get_history_item
from turtle import color, end_fill
#from cv2 import line
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
#from iexfinance.stocks import get_historical_data
import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import date
from datetime import datetime

#Día actual
today = date.today()


#FASE 1: Obtención de los Datos

Activo="COP=X"
FechaIni="2019-01-01"
FechaFin=today


df=yf.download(Activo,FechaIni,FechaFin)
print(df.info())

trace_close=go.Scatter(x=list(df.index),
                       y=list(df.Close),
                       name="Close",
                       line=dict(color="#f44242"))


trace_high=go.Scatter(x=list(df.index),
                       y=list(df.High),
                       name="High",
                       line=dict(color="#f44242"))

data=[trace_close]
layout=dict(title=Activo,
       showlegend=False)

fig = dict(data=data, layout=layout)


app= dash.Dash(__name__)

app.layout=html.Div([

html.H1(children="DASHBOARD TEST"),
html.Label("DASH GRAPH"),
html.Div([
dcc.Input(
    id="stock-input",
    placeholder="Enter a stock to be charter",
    type="text",
    value="SPY"
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
                figure={
                    "data":[trace_close],
                    "layout":{
                        "title":"Close Graph"
                    }
                }

            )
        ], className="six columns"),

        html.Div([
            dcc.Graph(
                id="graph_high",
                figure={
                    "data":[trace_high],
                    "layout":{
                        "title":"High Graphs"
                    }
                }

            )
        ], className="six columns")
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


@app.callback(dash.dependencies.Output("graph_close","figure")
            [dash.dependencies.Input("stock-input","value")]
            )


if __name__=="__main__":
    app.run_server(debug=True)