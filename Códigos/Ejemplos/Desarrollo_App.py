from multiprocessing import Value
from tkinter.tix import Select
import talib as ta
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import datetime
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

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
    Data['SMA 100']=ta.EMA(Data['Close'].values,100)

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

LastYear=current-datetime.timedelta(days=365*3)
ly=str(LastYear.year)+"-"+str(LastYear.month)+"-"+str(LastYear.day)

app = dash.Dash(__name__)

colors={
    'background':'#2E3442',
    'text':'#D0CFCF',
    'titles':'White'
}

def signal(data):
    compra=[]
    venta=[]
    condicion=0

    print(len(data))

    for dia in range(len(data)):
        
        if data["SMA 30"][dia]>data["SMA 100"][dia]:
            if condicion!=1:
                compra.append(data.Close[dia])
                venta.append(np.nan)
                condicion=1
            else:
                compra.append(np.nan)
                venta.append(np.nan)
        elif data["SMA 30"][dia]<data.Close[dia]:
            if condicion!=-1:
                venta.append(data.Close[dia])
                compra.append(np.nan)
                condicion=-1
            else:
                compra.append(np.nan)
                venta.append(np.nan)
        else:
             compra.append(np.nan)
             venta.append(np.nan)

    return (compra,venta)

fig=go.Figure()

fig.update_layout(

        showlegend=False,
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font_color=colors['titles'])

fig.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')
    
fig.update_yaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')


#Layout de la App

app.layout = html.Div([
    html.Div(
        children=[

        dcc.Store(id='store-data', data=[], storage_type='memory'),

        html.H2("PARÁMETROS DE ENTRADA"),  
        html.H3("Introduzca un Activo"),
        dcc.Input(id='input', value='COP=X', type='text', style={'marginRight':'10px'}),
        html.H3("Fecha Inicio"),
        dcc.Input(id='start', value=ly, type='text', style={'marginRight':'10px'}),
        html.H3("Fecha Final"),
        dcc.Input(id='end', value=cur, type='text', style={'marginRight':'10px'}),

        html.H3("Escoja un Indicador de Tendencia"),
        dcc.Dropdown(id="IndSelectTen",
            options={
                "SMA 30":"SMA 30",
                "SMA 100":"SMA 100",
                "Bollinger":"Bollinger",
                "SMA30_SMA100":"SMA 30 vs SMA 100"
                },
                value="SMA 30",
                searchable=False
        ),

        html.H3("Otras Opciones"),
        dcc.Checklist(id="OtrasOpc",
            options={
                "CV":"Compra / Venta"
            },
            labelStyle={'color':colors['text']}),
        
        html.H3("Escoja un Indicador Oscilatorio"),
        dcc.Dropdown(id="IndSelectOsc",
            options={
                "ADX":"ADX",
                "RSI":"RSI"
                }, 
            value="ADX",
            searchable=False
        ),

        html.Div(
            [
            dcc.Graph(id='ind-tendencias',figure=fig),
            dcc.Graph(id='ind-oscilatorios',figure=fig),
            ],
        ),
        
        html.Div(id='Estado Final'),
        html.H3(id="EstadoIni"),
        html.H3(id="EstadoFin")

                ]
    ,style={'padding': 10, 'flex': 1})

                    ])

#Estado Inicial

@app.callback(
    Output('EstadoIni','children'),
    Input('input','value')
)
def Estado(input_value):
    return "Estado: Descargando "+input_value

#Descarga

@app.callback(
    Output('store-data','data'),
    Input("start", "value"),
    Input("end", "value"),
    Input('input', 'value')
)
def update_value(cur, ly, input_data):

    df=obtencionDatos(input_data,'yahoo',cur,ly)
    Data=Indicadores(df)

    #FASE 2: Refinación de los datos

    """
    print(Data.info())
    print(Data.head())
    print(Data.describe())
    print(Data[Data.duplicated(keep='first')])
    """

    return Data.to_dict('records')

#Graficos de Tendencias

@app.callback(
    Output('ind-tendencias', 'figure'),
    Output('EstadoFin','children'),
    Input('IndSelectTen','value'),
    Input('store-data','data'),
    Input('input','value'),
    Input('OtrasOpc','value')
)

def PlotTen(SelectTen, data, input_data, Opc):

    df=pd.DataFrame(data)
    fig = go.Figure()

    fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df.Close,
                    marker_color='Gold'
                    ))

    fig.update_layout(
        title={
                'text': "Cierre para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                })

    if pd.isnull(Opc):
        print("Está en Null")
    elif len(Opc)==0:
        print("Está en 0")
    else:

        Sen=signal(df)
        df["Compra"]=Sen[0]
        df["Venta"]=Sen[1]

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df.Close,
                    marker_color='Gold'
                    ))

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["SMA 30"],
                    
                    marker_color='#F23E08'
                    ))

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["SMA 100"],
                    
                    marker_color='#F23E08'
                    ))

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df['Compra'],
                    
                    marker=dict(
                    color='LightSkyBlue',
                    size=20,
                    line=dict(
                    color='MediumPurple',
                    width=2
            )
        )
                    ))

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df['Venta'],
                    
                    marker=dict(
                    color='LightSkyBlue',
                    size=20,
                    line=dict(
                    color='MediumPurple',
                    width=2
            )
        )
                    ))

        fig.update_layout(
            title={
                'text': SelectTen+" para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                }
         )


    if SelectTen=="Bollinger":

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["upper_band"],
                    marker_color='#F23E08',
                    fill=None
                    ))

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["lower_band"],
                    marker_color='#F23E08',
                    fill='tonexty'
                    ))

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df.Close,
                marker_color='Gold'))

        fig.update_layout(
        title={
                'text': "Bandas de Bollinguer para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                })

    elif SelectTen=="SMA30_SMA100":

         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df.Close,
                    marker_color='Gold'
                    ))

         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["SMA 30"],
                    
                    marker_color='#F23E08'
                    ))

         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["SMA 100"],
                    
                    marker_color='#F23E08'
                    ))


         fig.update_layout(
            title={
                'text': SelectTen+" para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                }
         )
    else:

         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df.Close,
                    marker_color='Gold'
                    ))

         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df[SelectTen],
                    
                    marker_color='#F23E08'
                    ))

         fig.update_layout(
            title={
                'text': SelectTen+" para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                }
         )

    fig.update_layout(

        showlegend=False,
        xaxis_title="Muestras",
        yaxis_title="Valor del Activo",
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font_color=colors['titles'],
        title_font_color=colors['titles'])

    fig.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')
    
    fig.update_yaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')

    return [fig,"Estado: Datos descargados"]



#Graficos Oscilatorios

@app.callback(
    Output('ind-oscilatorios', 'figure'),
    Input('IndSelectOsc','value'),
    Input('store-data','data'),
    Input('input','value')
)
def PlotOsc(SelectOsc, data, input_data):
    
    df=pd.DataFrame(data)
    fig = go.Figure()

    if SelectOsc=="ADX":
         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df[SelectOsc],
                    marker_color='Gold',
                    fill='tonexty'      
                    ))

    elif SelectOsc=="RSI":
         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df[SelectOsc],
                    marker_color='Gold',
                    fill=None      
                    ))

    fig.update_layout(
         title={
                'text': SelectOsc+" para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                },
         yaxis_title=SelectOsc+" del Activo")

    fig.update_layout(

        showlegend=False,
        xaxis_title="Muestras",
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font_color=colors['titles'],
        title_font_color=colors['titles'])

    fig.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')
    
    fig.update_yaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)