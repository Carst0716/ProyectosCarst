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
import dash_bootstrap_components as dbc

#DASH: 100%

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


#FASE 4:  Construcción de la Dashboard

current = datetime.datetime.now()
cur=str(current.year)+"-"+str(current.month)+"-"+str(current.day)

LastYear=current-datetime.timedelta(days=365*5)
ly=str(LastYear.year)+"-"+str(LastYear.month)+"-"+str(LastYear.day)

app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

Entradas=html.Div(

        children=
    [

        dcc.Store(id='store-data', data=[], storage_type='memory'),

        html.Div([
        html.Div("Introduzca un Activo", className="textInput"),
        dcc.Input(id='input', value='COP=X', type='text', className="input")
                ], className="inputsBox"),

        html.Div([
        html.Div("Fecha Inicio", className="textInput"),
        dcc.Input(id='start', value=ly, type='text', className="input")
        ], className="inputsBox"),

        html.Div([
        html.Div("Fecha Final", className="textInput"),
        dcc.Input(id='end', value=cur, type='text', className="input")
        ], className="inputsBox")
        

    ],className="BoxEntradas")

#dbc.Row(dbc.Col(html.H3("ANÁLISIS TÉCNICO BASADO EN TRADING ALGORÍTMICO", className="Titulo"))),
       

Titulo=html.Div(

        children=
    [

        html.Div("Análisis Técnico de Activos FOREX para la Toma de Decisiones", className="Titulo")

    ])

Tendencias=html.Div(

        children=
    [

    dcc.Graph(id='ind-tendencias',figure=fig),
    

    ],className="BoxGraph")

SugTendencias=html.Div(

        children=
    [
    
    html.Div(
        [
    html.Div("Actual: ",id="ActualTen",className="SugTen"),
    html.Div("Máximo: ",id="MaximoTen",className="SugTen"),
    html.Div("Mínimo: ",id="MinimoTen",className="SugTen"),
    html.Div("Promedio: ",id="PromedioTen",className="SugTen"),
    html.Div("D. Estandar: ",id="StdTen",className="SugTen"),
    html.Div("INDICADORES",className="SugTen"),
    html.Div(dcc.Dropdown(id="IndSelectTen",
    options={
             "Divisa":"Divisa",
             "SMA 30":"SMA 30",
             "SMA 100":"SMA 100",
             "Bollinger":"Bollinger",
             "SMA30 vs SMA100":"SMA 30 vs SMA 100"
            },
        value="Divisa",
        searchable=False
            ,className="SugTenInd")),

    html.Div("SEÑALES",className="SugTen"),
    html.Div(dcc.Checklist(id="OtrasOpc",
    options={
            "CV":"Compra / Venta"
            },
    labelStyle={'color':colors['text']}),className="SugTenOption")
        ],className="SugBoxTen"
    ),

    ],className="BoxSugTen")

indADX=html.Div(

        children=
    [

    dcc.Graph(id='indADX',figure=fig)

    ],className="BoxGraph")
SugADX=html.Div(

        children=
    [
    
    html.Div(
        [
    html.Div("Actual: ",id="ActualADX",className="SugTen"),
    html.Div("Máximo: ",id="MaximoADX",className="SugTen"),
    html.Div("Mínimo: ",id="MinimoADX",className="SugTen"),
    html.Div("Promedio: ",id="PromedioADX",className="SugTen"),
    html.Div("D. Estandar: ",id="StdADX",className="SugTen"),
    html.Div("Fuerza: ",id="Fuerza",className="SugTen")
        ],className="SugBox"
    ),

    ],className="BoxSug")

indRSI=html.Div(

        children=
    [

    dcc.Graph(id='indRSI',figure=fig)

    ],className="BoxGraph")
SugRSI=html.Div(

        children=
    [
    
    html.Div(
        [
    html.Div("Actual: ",id="ActualRSI",className="SugTen"),
    html.Div("Máximo: ",id="MaximoRSI",className="SugTen"),
    html.Div("Mínimo: ",id="MinimoRSI",className="SugTen"),
    html.Div("Promedio: ",id="PromedioRSI",className="SugTen"),
    html.Div("D. Estandar: ",id="StdRSI",className="SugTen"),
    html.Div("Tendencia: ",id="Tendencia",className="SugTen"),
        ],className="SugBox"
    ),

    ],className="BoxSug")

row = html.Div(
    [
        
        dbc.Row(
            [
                dbc.Col(Entradas),
                dbc.Col(Titulo)
                
            ]
        ),

        dbc.Row(
            [
                dbc.Col(Tendencias),
                dbc.Col(SugTendencias),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(indRSI),
                dbc.Col(SugRSI),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(indADX),
                dbc.Col(SugADX),
            ]
        ),

        dbc.Row(dbc.Col(
            
            html.Div([

                html.Div("Carlos M. Ariza - Técnico en Programación para Analítica de Datos - SENA Marzo de 2022"),
                html.Div("ariza.cm@gmail.com  -  3176065917")
            
            ],className="Creditos"))),

    ])

app.layout = dbc.Container(row, class_name="BoxMain")


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

    print(df)

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
    Output('ActualTen','children'),
    Output('MaximoTen','children'),
    Output('MinimoTen','children'),
    Output('PromedioTen','children'),
    Output('StdTen','children'),

    Output('ActualADX','children'),
    Output('MaximoADX','children'),
    Output('MinimoADX','children'),
    Output('PromedioADX','children'),
    Output('StdADX','children'),
    Output('Fuerza','children'),

    Output('ActualRSI','children'),
    Output('MaximoRSI','children'),
    Output('MinimoRSI','children'),
    Output('PromedioRSI','children'),
    Output('StdRSI','children'),
    Output('Tendencia','children'),

    Output('ind-tendencias', 'figure'),
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
                    marker_color='#7B7E8D',
                    fill=None
                    ))

        fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["lower_band"],
                    marker_color='#7B7E8D',
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

    #SALIDAS

    #Tendencia

    ActualTen=list(df["Close"])[-1]
    MaximoTen=df["Close"].max()
    MinimoTen=df["Close"].min()
    PromedioTen=df["Close"].mean()
    StdTen=df["Close"].std()

    """    
    x0 = df.index[0]       
    x1 = df.index[-1] 
    fig.add_shape(type="line",
            x0=x0, y0=PromedioTen, x1=x1, y1=PromedioTen,
            line=dict(color="Green",width=1),
        )
        
    """

    #RSI
    
    ActualRSI=list(df["RSI"])[-1]
    MaximoRSI=df["RSI"].max()
    MinimoRSI=df["RSI"].min()
    PromedioRSI=df["RSI"].mean()
    StdRSI=df["RSI"].std()

    #ADX
    
    ActualADX=list(df["ADX"])[-1]
    MaximoADX=df["ADX"].max()
    MinimoADX=df["ADX"].min()
    PromedioADX=df["ADX"].mean()
    StdADX=df["ADX"].std()

    RsiF=ActualRSI
    ADxF=ActualADX

    
    if 30<=RsiF<=70: #[30 70]
        if 0<=ADxF<=25: #[0 25]
            Dec="Baja"
            ColorDec=colors_Rec['Moderada']
            Ten="Estable"
        
        elif 25<ADxF<=50: #[25 50]
            Dec="Media"
            ColorDec=colors_Rec['Moderada']
            Ten="Estable"
        
        elif 50<ADxF<=75: #[50 75]
            Dec="Alta"
            ColorDec=colors_Rec['Moderada']
            Ten="Estable"
        
        elif 75<ADxF<=100: #[75 100]
            Dec="Muy Alta"
            ColorDec=colors_Rec['Moderada']
            Ten="Estable"

        else:
            Dec="No Definido"
            ColorDec=colors_Rec['NoDefinido']
            Ten="Estable"
    
    elif RsiF<30:
        if 0<=ADxF<=25: #[0 25]
            Dec="Baja"
            ColorDec=colors_Rec['SobreVenta']
            Ten="Alcista"
        
        elif 25<ADxF<=50: #[25 50]
            Dec="Media"
            ColorDec=colors_Rec['SobreVenta']
            Ten="Alcista"
        
        elif 50<ADxF<=75: #[50 75]
            Dec="Alta"
            ColorDec=colors_Rec['SobreVenta']
            Ten="Alcista"
        
        elif 75<ADxF<=100: #[75 100]
            Dec="Muy Alta"
            ColorDec=colors_Rec['SobreVenta']
            Ten="Alcista"

        else:
            Dec="No Definido"
            ColorDec=colors_Rec['NoDefinido']
    
    elif RsiF>70:
        if 0<=ADxF<=25: #[0 25]
            Dec="Baja"
            ColorDec=colors_Rec['SobreCompra']
            Ten="Bajista"
        
        elif 25<ADxF<=50: #[25 50]
            Dec="Media"
            ColorDec=colors_Rec['SobreCompra']
            Ten="Bajista"
        
        elif 50<ADxF<=75: #[50 75]
            Dec="Alta"
            ColorDec=colors_Rec['SobreCompra']
            Ten="Bajista"
        
        elif 75<ADxF<=100: #[75 100]
            Dec="Muy Alta"
            ColorDec=colors_Rec['SobreCompra']

        else:
            Dec="No Definido"
            ColorDec=colors_Rec['NoDefinido']
    
    return [
            "Actual: "+str(int(ActualTen)),
            "Máximo: "+str(int(MaximoTen)),
            "Mínimo: "+str(int(MinimoTen)),
            "Promedio: "+str(int(PromedioTen)),
            "D. Estandar: "+str(int(StdTen)),

            "Actual: "+str(int(ADxF))+" %",
            "Máximo: "+str(int(MaximoADX)),
            "Mínimo: "+str(int(MinimoADX)),
            "Promedio: "+str(int(PromedioADX)),
            "D. Estandar: "+str(int(StdADX)),
            "Fuerza: "+Dec,

            "Actual: "+str(int(RsiF))+" %",
            "Máximo: "+str(int(MaximoRSI)),
            "Mínimo: "+str(int(MinimoRSI)),
            "Promedio: "+str(int(PromedioRSI)),
            "D. Estandar: "+str(int(StdRSI)),
            "Tendencia: "+Ten,
            
            fig

            ]

#Graficos Oscilatorios

@app.callback(
    Output('indADX', 'figure'),
    Input('store-data','data'),
    Input('input','value')
)
def PlotADX(data, input_data):
    
    df=pd.DataFrame(data)
    fig = go.Figure()

    fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["ADX"],
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

    fig.update_layout(
         title={
                'text':"ADX para "+input_data,
                'y':0.9, # new
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top' # new
                },
         yaxis_title="ADX del Activo",
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

@app.callback(
    Output('indRSI', 'figure'),
    Input('store-data','data'),
    Input('input','value')
)
def PlotRSI(data, input_data):
    
         df=pd.DataFrame(data)
         fig = go.Figure()

         fig.add_trace(
            go.Scatter(
                    x=df.index,
                    y=df["RSI"],
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
                        'text': "RSI para "+input_data,
                        'y':0.9, # new
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top' # new
                        },
                yaxis_title="RSI del Activo",
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