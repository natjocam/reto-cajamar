
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import geopandas as gpd
import pandas as pd

from utils import CombineTop10

app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv("data/new_files/ds_completo.csv")
geodata = gpd.read_file("data/new_files/regiones_simple.json").set_index("name")

app.layout = html.Div(children=[
    html.H1(children='Atmira Pharma Data Analysis'),

    dcc.Dropdown(
        options=df["marca_value"].sort_values().unique(),
        value=df["marca_value"][0],
        id="marca-input",
    ),

    html.Div([
        html.Div([
            html.H3('Sales by area'),
            dcc.Graph(id='area-graph', figure={},)
        ], className="six columns"),

        html.Div([
            html.Div([
                html.H3('Sales in time'),
                dcc.Graph(id='time-graph', figure={})
            ], className ="row"),

            html.Div([
                html.Div([
                    html.H3('Top products'),
                    dcc.Graph(id='products-graph', figure={})
                ], className ="six columns"),

                html.Div([
                    html.H3('Top clients'),
                    dcc.Graph(id='customers-graph', figure={})
                ], className ="six columns")
            ], className="row"), 

        ], className="six columns")
    ], className="row") 
])


@app.callback(
    Output("products-graph", "figure"),
    Input("marca-input", "value")
)
def update_graph(marca):
    _df = df.loc[df.marca_value == marca].groupby("name")[["sales_EUR"]].sum().reset_index().sort_values("sales_EUR", ascending=False).head(5)
    fig = px.pie(_df, names="name", values="sales_EUR")
    fig.update_layout(legend=dict(
        yanchor="top",
        y=-0.1,
        xanchor="left",
        x=0.0
    ), height=400)
    return fig

@app.callback(
    Output("customers-graph", "figure"),
    Input("marca-input", "value")
)
def update_graph(marca):
    _df = df.loc[df.marca_value == marca].groupby("customer_id")[["sales_EUR"]].sum().reset_index().sort_values("sales_EUR", ascending=False).head(5)
    fig = px.pie(_df, names="customer_id", values="sales_EUR")
    fig.update_layout(legend=dict(
        yanchor="top",
        y=-0.1,
        xanchor="left",
        x=0.0
    ), height = 400)
    return fig

@app.callback(
    Output("time-graph", "figure"),
    Input("marca-input", "value")
)
def update_graph(marca):
    _df = df.loc[df.marca_value == marca].groupby("date")[["sales_EUR"]].sum().reset_index()
    fig = px.line(_df, x="date", y="sales_EUR")
    fig.update_layout(height=200)
    return fig

@app.callback(
    Output("area-graph", "figure"),
    Input("marca-input", "value")
)
def update_graph(marca):
    _df = df.loc[df.marca_value == marca].groupby("area")[["sales_EUR"]].sum()
    _df = geodata.join(_df)
    fig= px.choropleth_mapbox(_df, geojson=_df.geometry, color="sales_EUR", locations=_df.index, 
        mapbox_style="carto-positron", zoom=4, center = {"lat": 40.64, "lon": -3.7},)
    fig.update_layout(height=600)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
