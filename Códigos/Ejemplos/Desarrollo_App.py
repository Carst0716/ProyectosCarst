from multiprocessing import Value
from statistics import mode
from tkinter.tix import Select
from matplotlib.pyplot import text
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


#DASH: 85%

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

LastYear=current-datetime.timedelta(days=365*5)
ly=str(LastYear.year)+"-"+str(LastYear.month)+"-"+str(LastYear.day)

app = dash.Dash(__name__)

colors={
    'background':'#282D39',
    'text':'#D0CFCF',
    'titles':'White'
}

def signal(data):
    compra=[]
    venta=[]
    condicion=0

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
                "Divisa":"Divisa",
                "SMA 30":"SMA 30",
                "SMA 100":"SMA 100",
                "Bollinger":"Bollinger",
                "SMA30 vs SMA100":"SMA 30 vs SMA 100"
                },
                value="Divisa",
                searchable=False
        ),

        html.H3("Señales"),
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
            value="RSI",
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
        html.H3(id="EstadoFin"),
        
        html.Div([
        html.Div(id="AporteADX",className="ADX"),
        html.Div(id="AporteRSI",className="RSI"),
        html.Div(id="Tendencia",className="Tendencia"),
        html.Div(id="Recomendacion",className="RecCompra")
        ],className="RecDIV")
                ])

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
    Output('Recomendacion','children'),
    Output('Recomendacion','style'),
    Output('AporteADX','children'),
    Output('AporteRSI','children'),
    Output('Tendencia','children'),
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

    if not pd.isnull(Opc) and not len(Opc)==0:

        Sen=signal(df)
        df["Compra"]=Sen[0]
        df["Venta"]=Sen[1]

        fig.add_trace(
            go.Scatter(
                    mode="markers",
                    x=df.index,
                    y=df['Compra'],
                    marker=dict(
            symbol='triangle-up',
            color='#01CD9A',
            size=20
            )
        )
                    )

        fig.add_trace(
            go.Scatter(
                    mode="markers",
                    x=df.index,
                    y=df['Venta'],
                    marker=dict(
            symbol='triangle-down',
            color='Red',
            size=20
            )
        )
                    )

        fig.update_layout(
            title={
                'text': SelectTen+" para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                }, xaxis_range=[0,max(df.index)]
         )

    if SelectTen=="Bollinger":

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["upper_band"],
                    marker_color='#124702',
                    fill=None
                    ))

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["lower_band"],
                    marker_color='#124702',
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

    elif SelectTen=="SMA30 vs SMA100":

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
    
    elif SelectTen=="Divisa":

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df.Close,
                    marker_color='Gold'
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

    colors_Rec={
        'Moderada':'#FFCC00',
        'SobreCompra':'#9ACD32',
        'SobreVenta':'#F64005',
        'NoDefinido':'#00197F'}

#TOMAR LA DECISIÓN...


    #Pesos por Indicador

    RsiF=list(df["RSI"])[-1]
    ADxF=list(df["ADX"])[-1]
    
    if 30<=RsiF<=70: #[30 70]
        if 0<=ADxF<=25: #[0 25]
            Dec="Estable con Volatilidad Moderada"
            ColorDec=colors_Rec['Moderada']
            Ten="Estable"
        
        elif 25<ADxF<=50: #[25 50]
            Dec="Fuerte con Volatilidad Moderada"
            ColorDec=colors_Rec['Moderada']
            Ten="Estable"
        
        elif 50<ADxF<=75: #[50 75]
            Dec="Muy Fuerte con Volatilidad Moderada"
            ColorDec=colors_Rec['Moderada']
            Ten="Estable"
        
        elif 75<ADxF<=100: #[75 100]
            Dec="Extremadamente Fuerte con Volatilidad Moderada"
            ColorDec=colors_Rec['Moderada']
            Ten="Estable"

        else:
            Dec="No Definido"
            ColorDec=colors_Rec['NoDefinido']
            Ten="Estable"
    
    elif RsiF<30:
        if 0<=ADxF<=25: #[0 25]
            Dec="Estable y en Sobreventa"
            ColorDec=colors_Rec['SobreVenta']
            Ten="Alcista"
        
        elif 25<ADxF<=50: #[25 50]
            Dec="Fuerte y en Sobreventa"
            ColorDec=colors_Rec['SobreVenta']
            Ten="Alcista"
        
        elif 50<ADxF<=75: #[50 75]
            Dec="Muy Fuerte y en Sobreventa"
            ColorDec=colors_Rec['SobreVenta']
            Ten="Alcista"
        
        elif 75<ADxF<=100: #[75 100]
            Dec="Extremadamente Fuerte y en Sobreventa"
            ColorDec=colors_Rec['SobreVenta']
            Ten="Alcista"

        else:
            Dec="No Definido"
            ColorDec=colors_Rec['NoDefinido']
    
    elif RsiF>70:
        if 0<=ADxF<=25: #[0 25]
            Dec="Estable y en Sobrecompra"
            ColorDec=colors_Rec['SobreCompra']
            Ten="Bajista"
        
        elif 25<ADxF<=50: #[25 50]
            Dec="Fuerte y en Sobrecompra"
            ColorDec=colors_Rec['SobreCompra']
            Ten="Bajista"
        
        elif 50<ADxF<=75: #[50 75]
            Dec="Muy Fuerte y en Sobrecompra"
            ColorDec=colors_Rec['SobreCompra']
            Ten="Bajista"
        
        elif 75<ADxF<=100: #[75 100]
            Dec="Extremadamente Fuerte y en Sobrecompra"
            ColorDec=colors_Rec['SobreCompra']

        else:
            Dec="No Definido"
            ColorDec=colors_Rec['NoDefinido']
    
    return [fig,
        "Estado: Datos descargados",
        Dec,
        {'background-color': ColorDec},"RSI: "+str(RsiF)[0:5]+" %","ADX: "+str(ADxF)[0:5]+" %",Ten]

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

         x0 = df.index[0]       
         x1 = df.index[-1] 
         fig.add_shape(type="line",
            x0=x0, y0=25, x1=x1, y1=25,
            line=dict(color="#F23E08",width=2),
        )

         x0 = df.index[0]       
         x1 = df.index[-1] 
         fig.add_shape(type="line",
            x0=x0, y0=50, x1=x1, y1=50,
            line=dict(color="#0DC1F7",width=2),
        )

        
         x0 = df.index[0]       
         x1 = df.index[-1] 
         fig.add_shape(type="line",
            x0=x0, y0=75, x1=x1, y1=75,
            line=dict(color="#3EF208",width=2)
        )

         fig.add_annotation(x=max(df.index)/4, y=75-7,
            text="MUY FUERTE",
            font=dict(
            family="Courier New, monospace",
            size=16,
            color="#FFFFFF"),
            showarrow=True,
            arrowhead=1,
            bordercolor="#2E3442",
            borderwidth=5,
            borderpad=4,
            bgcolor="#3EF208",
            opacity=0.8)

         fig.add_annotation(x=max(df.index)/4, y=50-7,
            text="FUERTE",
            font=dict(
            family="Courier New, monospace",
            size=16,
            color="#FFFFFF"),
            showarrow=True,
            arrowhead=1,
            bordercolor="#2E3442",
            borderwidth=5,
            borderpad=4,
            bgcolor="#0DC1F7",
            opacity=0.8)

         fig.add_annotation(x=max(df.index)/4, y=25-7,
            text="AUSENCIA",
            font=dict(
            family="Courier New, monospace",
            size=16,
            color="#FFFFFF"),
            showarrow=True,
            arrowhead=1,
            bordercolor="#2E3442",
            borderwidth=5,
            borderpad=4,
            bgcolor="#F23E08",
            opacity=0.8)

    elif SelectOsc=="RSI":
         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df[SelectOsc],
                    marker_color='Gold',
                    fill=None      
                    ))

         x0 = df.index[0]       
         x1 = df.index[-1] 
         fig.add_shape(type="line",
            x0=x0, y0=30, x1=x1, y1=30,
            line=dict(color="#F23E08",width=2),
        )

         x0 = df.index[0]       
         x1 = df.index[-1] 
         fig.add_shape(type="line",
            x0=x0, y0=70, x1=x1, y1=70,
            line=dict(color="#3EF208",width=2),
        )

         fig.add_annotation(x=max(df.index)/4, y=70-7,
            text="SOBRECOMPRA",
            font=dict(
            family="Courier New, monospace",
            size=16,
            color="#FFFFFF"),
            showarrow=True,
            arrowhead=1,
            bordercolor="#2E3442",
            borderwidth=5,
            borderpad=4,
            bgcolor="#3EF208",
            opacity=0.8)

         fig.add_annotation(x=max(df.index)/4, y=30-14,
            text="SOBREVENTA",
            font=dict(
            family="Courier New, monospace",
            size=16,
            color="#FFFFFF"),
            showarrow=True,
            arrowhead=1,
            bordercolor="#2E3442",
            borderwidth=5,
            borderpad=4,
            bgcolor="#F23E08",
            opacity=0.8)

    fig.update_layout(
         title={
                'text': SelectOsc+" para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                },
         yaxis_title=SelectOsc+" del Activo",
         yaxis_range=[0,100])

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