import dash_bootstrap_components as dbc
from dash import html
import dash
from dash import dcc
from dash import html

app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

import dash_bootstrap_components as dbc
from dash import html

row = html.Div(
    [
        dbc.Row(dbc.Col(html.Div("Titulo de la DashBoard", className="Box"))),
       
        dbc.Row(
            [
                dbc.Col(html.Div("Entradas", className="Box")),
                dbc.Col(html.Div("Grafico Tendencias", className="Box")),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(html.Div("Controles", className="Box")),
                dbc.Col(html.Div("Grafico ADX", className="Box")),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(html.Div("Salidas", className="Box")),
                dbc.Col(html.Div("Grafico RSI", className="Box")),
            ]
        ),

        dbc.Row(dbc.Col(html.Div("Créditos", className="Box"))),

    ]
, className="BoxMain")

app.layout = dbc.Container(row)

if __name__ == '__main__':
    app.run_server(debug=True)