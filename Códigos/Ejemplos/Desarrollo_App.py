from multiprocessing import Value
from tkinter.tix import Select
import talib as ta
import pandas as pd
import pandas_datareader.data as web
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
        dcc.Checklist(id="IndSelectTen",
            options={
                "SMA 30":"SMA 30",
                "SMA 100":"SMA 100",
                "Bollinger":"Bollinger",
                "SMA30_SMA100":"SMA 30--SMA 100"
                }, 
                labelStyle=
                {
                    'display': 'inline-block',
                    'color': colors['text'],
                }
        ),
        
        html.H3("Escoja un Indicador Oscilatorio"),
        dcc.Checklist(id="IndSelectOsc",
            options={
                "ADX":"ADX",
                "RSI":"RSI"
                }, 
                labelStyle=
                {
                    'display': 'inline-block',
                    'color': colors['text'],
                },
            value=["ADX"]
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
    
    print(Data.info())

    """
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
    Input('input','value')
)
def PlotTen(SelectTen, data, input_data):

    df=pd.DataFrame(data)
    fig = go.Figure()
    
    if pd.isnull(SelectTen):

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

    elif len(SelectTen)==0:

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
        

    elif "Bollinger" in SelectTen:

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

    elif "SMA30_SMA100" in SelectTen:

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
                'text': SelectTen[0]+" para "+input_data,
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
                    y=df[SelectTen[0]],
                    
                    marker_color='#F23E08'
                    ))
         fig.update_layout(
            title={
                'text': SelectTen[0]+" para "+input_data,
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
    
    if not pd.isnull(SelectOsc) and not len(SelectOsc)==0:

        if SelectOsc[0]=="ADX":
         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df[SelectOsc[0]],
                    marker_color='Gold',
                    fill='tonexty'      
                    ))

        elif SelectOsc[0]=="RSI":
         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df[SelectOsc[0]],
                    marker_color='Gold',
                    fill=None      
                    ))

         fig.update_layout(
         title={
                'text': SelectOsc[0]+" para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                },
         yaxis_title=SelectOsc[0]+" del Activo")

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