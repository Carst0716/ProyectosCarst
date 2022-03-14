import pandas_datareader.data as web
import datetime
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

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

    df = web.DataReader(input_data, 'yahoo', cur, ly)
    df.reset_index(inplace=True)
    df.set_index("Date", inplace=True)
    #df = df.drop("Symbol", axis=1)

    print(df.info())
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