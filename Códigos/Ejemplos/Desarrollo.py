import talib as ta
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output



#FASE 1: Obtención de los Datos

def obtencionDatos(input_data,motor,cur,ly):
    df = web.DataReader(input_data, motor, cur, ly)
    df.reset_index(inplace=True)
    df.set_index("Date", inplace=True)
    #df = df.drop("Symbol", axis=1)

    return df

def Indicadores(Data):
    #FASE 3: Análisis de datos y calculo de indicadores

    #Media móvil para 30 muestras
    Data['SMA 30']=ta.SMA(Data['Close'].values,30)

    #Media móvil para 100 muestras
    Data['EMA 100']=ta.EMA(Data['Close'].values,100)

    #Bandas de bollinger para un periodo de 30 muestras
    Data['upper_band'], Data['middle_band'], Data['lower_band']=ta.BBANDS(Data['Close'],timeperiod=20)

    #ADX: Average Directional Movement Index
    Data['ADX']=ta.ADX(Data['High'],Data['Low'],Data['Close'],timeperiod=14)

    #RSI: Relative strength index
    Data['RSI']=ta.RSI(Data['Close'],14)
    
    return Data


#FASE 4:  Construcción de la Dashboard

current = datetime.datetime.now()
cur=str(current.year)+"-"+str(current.month)+"-"+str(current.day)

LastYear=current-datetime.timedelta(days=365)
ly=str(LastYear.year)+"-"+str(LastYear.month)+"-"+str(LastYear.day)

app = dash.Dash()

colors={
    'background':'#111111',
    'text':'#7FDBFF'
}

app.layout = html.Div([
    html.Div(
        children=[
        html.H2("PARÁMETROS DE ENTRADA"),  
        html.H3("Introduzca un Activo"),
        dcc.Input(id='input', value='COP=X', type='text', style={'marginRight':'10px'}),
        html.H3("Fecha Inicio"),
        dcc.Input(id='start', value=ly, type='text', style={'marginRight':'10px'}),
        html.H3("Fecha Final"),
        dcc.Input(id='end', value=cur, type='text', style={'marginRight':'10px'}),
        html.Div(id='output-graph')
                ]
    ,style={'padding': 10, 'flex': 1})

                    ],style={'display': 'flex', 'flex-direction': 'column'})


@app.callback(
    Output('output-graph', 'children'),
    Input("start", "value"),
    Input("end", "value"),
    Input('input', 'value')
)


def update_value(cur, ly, input_data):

    print("Descargando datos...")

    df=obtencionDatos(input_data,'yahoo',cur,ly)
    Data=Indicadores(df)

    #FASE 2: Refinación de los datos

    print(Data.head())
    print(Data.info())
    print(Data.describe())
    print(Data[Data.duplicated(keep='first')])

    print(" ")
    print("Datos descargados...")

    return html.Div(
        [dcc.Graph(
        id='example-graph',
        figure=
        {
            'data': 
            [
                {'x': df.index, 'y': df.Close, 'type': 'line', 'name': input_data},
            ],
            'layout': 
            {
                'title': "Cierre para "+input_data
            }
        }
    ),
        dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        {'x': df.index, 'y': df.Open, 'type': 'line', 'name': input_data},
                    ],
                    'layout': {
                        'title': "Apertura para "+input_data
                    }
                }
            )

    ], style={
        'backgroundColor': colors['background']}
            )


if __name__ == '__main__':
    app.run_server(debug=True)