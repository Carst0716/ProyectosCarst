import pandas_datareader.data as web
import datetime
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

#start = datetime.datetime(2021, 1, 1)
#end = datetime.datetime.now()

app = dash.Dash()

app.layout = html.Div(children=[
    html.Div(children='''
        Introduzca un Activo:
    '''),
    dcc.Input(id='input', value='SPY', type='text'),
    dcc.Input(id='start', value='2021-01-01', type='text'),
    dcc.Input(id='end', value='2022-01-01', type='text'),
    html.Div(id='output-graph'),
])


@app.callback(
    Output('output-graph', 'children'),
    [Input("start", "value"),
    Input("end", "value"),
    Input('input', 'value')]
)
def update_value(input_data):
    df = web.DataReader(input_data, 'yahoo', start, end)
    df.reset_index(inplace=True)
    df.set_index("Date", inplace=True)
    #df = df.drop("Symbol", axis=1)

    return html.Div([dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': df.index, 'y': df.Close, 'type': 'line', 'name': input_data},
            ],
            'layout': {
                'title': input_data
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
                        'title': input_data
                    }
                }
            )

    ])


if __name__ == '__main__':
    app.run_server(debug=True)