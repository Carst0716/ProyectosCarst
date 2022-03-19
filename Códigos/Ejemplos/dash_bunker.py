import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Checklist(
            id="checklist",
            options=[
                {"label": "New York City", "value": "NYC"},
                {"label": "Montréal", "value": "MTL"},
                {"label": "San Francisco", "value": "SF"},
            ],
            labelStyle={"display": "block"},
            value=[],
        ),
        html.Button("load", id="load-button", n_clicks=0),
    ]
)


@app.callback(Output("checklist", "value"), Input("load-button", "n_clicks"))
def change_values(n_clicks):
    return ["SF"] if n_clicks > 0 else []




if __name__ == '__main__':
    app.run_server(debug=True)