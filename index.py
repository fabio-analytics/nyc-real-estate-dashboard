from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from app import app

# =======================================================
# O SEGREDO PRO RENDER: Declarar o server aqui no index!
# =======================================================
server = app.server

# Componentes
from _map import *
from _controllers import *
from _histogram import *

# =======================================
# Data Ingestion 
# =======================================
df_data = pd.read_csv("dataset/cleaned_data.csv", index_col=0)

mean_lat = df_data["LATITUDE"].mean()
mean_long = df_data["LONGITUDE"].mean()

df_data["size_m2"] = df_data["GROSS SQUARE FEET"] / 10.764
df_data = df_data[df_data["YEAR BUILT"] > 0]
df_data["SALE DATE"] = pd.to_datetime(df_data["SALE DATE"])

df_data.loc[df_data["size_m2"] > 10000, "size_m2"] = 10000
df_data.loc[df_data["SALE PRICE"] > 50000000, "SALE PRICE"] = 50000000
df_data.loc[df_data["SALE PRICE"] < 100000, "SALE PRICE"] = 100000

# ================================
# Criando os Cards de KPI (Design Sofisticado)
# ================================
def criar_card(titulo, id_valor, cor_texto):
    return dbc.Card([
        dbc.CardBody([
            html.H6(titulo, className="text-muted text-uppercase text-center", style={"font-size": "12px", "letter-spacing": "1px"}),
            html.H4(id=id_valor, className=f"{cor_texto} text-center font-weight-bold", style={"margin-bottom": "0px"})
        ])
    ], style={"background-color": "rgba(255, 255, 255, 0.05)", "border": "1px solid rgba(255, 255, 255, 0.1)", "border-radius": "15px", "box-shadow": "0 4px 15px rgba(0,0,0,0.3)"})

kpi_row = dbc.Row([
    dbc.Col(criar_card("Total de Imóveis", "kpi-total", "text-info"), md=3),
    dbc.Col(criar_card("Preço Médio", "kpi-mean", "text-warning"), md=3),
    dbc.Col(criar_card("Preço Mediano", "kpi-median", "text-success"), md=3),
    dbc.Col(criar_card("Preço por m²", "kpi-m2", "text-danger"), md=3),
], className="mb-4 mt-2")


# ================================
# Template Layout Atualizado
# ================================
app.layout = dbc.Container(
    children=[
        dbc.Row([
            # Coluna da Esquerda (Filtros)
            dbc.Col([
                controllers
            ], md=3, style={"padding-right": "25px", "padding-left": "25px", "padding-top": "50px"}),
            
            # Coluna da Direita (Gráficos e KPIs)
            dbc.Col([
                kpi_row, # <-- NOSSOS KPIS ESTÃO AQUI!
                dbc.Row([dbc.Col([map], md=12)], className="mb-4"), # Mapa ocupando tudo
                dbc.Row([
                    dbc.Col([hist], md=6), # Histograma de um lado
                    dbc.Col([dcc.Graph(id='time-series-graph')], md=6) # Série Temporal do outro!
                ]),
            ], md=9, style={"padding-top": "20px"}),
        ])
    ], fluid=True, style={"background-color": "#0a0a0a"} # Fundo escuro premium
)

# ========================================================
# Callbacks (Agora atualiza tudo de uma vez!)
# ========================================================
@app.callback(
    [Output('hist-graph', 'figure'), 
     Output('map-graph', 'figure'),
     Output('time-series-graph', 'figure'),
     Output('kpi-total', 'children'),
     Output('kpi-mean', 'children'),
     Output('kpi-median', 'children'),
     Output('kpi-m2', 'children')],
    [Input('location-dropdown', 'value'), 
     Input('slider-square-size', 'value'), 
     Input('dropdown-color', 'value')]            
)
def update_dash(location, square_size, color_map):
    
    # Prevenção de erros vazios
    if color_map is None: color_map = "SALE PRICE"
        
    # Filtragem
    if location is None:
        df_intermediate = df_data.copy()
    else:
        size_limit = slider_size[square_size] if square_size is not None else df_data["GROSS SQUARE FEET"].max()
        df_intermediate = df_data[df_data["BOROUGH"] == location] if location != 0 else df_data.copy()
        df_intermediate = df_intermediate[df_intermediate["GROSS SQUARE FEET"] <= size_limit]

    # ==========================
    # Cálculos dos KPIs
    # ==========================
    num_imoveis = len(df_intermediate)
    val_medio = df_intermediate["SALE PRICE"].mean()
    val_mediano = df_intermediate["SALE PRICE"].median()
    val_m2 = (df_intermediate["SALE PRICE"] / df_intermediate["size_m2"]).mean()

    # Formatação bonitona
    kpi_total_text = f"{num_imoveis:,}".replace(",", ".")
    kpi_mean_text = f"$ {val_medio:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    kpi_median_text = f"$ {val_mediano:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    kpi_m2_text = f"$ {val_m2:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".") if not pd.isna(val_m2) else "$ 0"

    # ==========================
    # Histogram
    # ==========================
    hist_fig = px.histogram(df_intermediate, x=color_map, opacity=0.75, color_discrete_sequence=['#22d3ee'])
    hist_layout = go.Layout(
        title=dict(text=f"Distribuição de {color_map}", font=dict(color="#ffffff", size=14)),
        margin=go.layout.Margin(l=10, r=0, t=40, b=20),
        showlegend=False, 
        template="plotly_dark", 
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)"
    )
    hist_fig.layout = hist_layout

    # ==========================
    # Time Series (NOVO)
    # ==========================
    df_ts = df_intermediate.groupby(df_intermediate["SALE DATE"].dt.to_period("M"))["SALE PRICE"].mean().reset_index()
    df_ts["SALE DATE"] = df_ts["SALE DATE"].dt.to_timestamp()
    
    ts_fig = px.line(df_ts, x="SALE DATE", y="SALE PRICE", color_discrete_sequence=['#f59e0b'])
    ts_fig.update_layout(
        title=dict(text="Evolução do Preço Médio", font=dict(color="#ffffff", size=14)),
        template="plotly_dark", 
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        margin=go.layout.Margin(l=10, r=10, t=40, b=20)
    )

    # ==========================
    # Map (AGORA COM HOVER SOFISTICADO)
    # ==========================
    px.set_mapbox_access_token("pk.eyJ1IjoiZmFiaW9ib29rMjMiLCJhIjoiY21tZ2l0em82MGkyOTJxcHZ3ejlubG1qcSJ9.zIpCBFZBYMrJ1OxwHMyAUg")
    
    map_fig = px.scatter_mapbox(
        df_intermediate, lat="LATITUDE", lon="LONGITUDE", color=color_map, 
        size="size_m2", size_max=20, zoom=10, opacity=0.6,
        hover_data={"LATITUDE": False, "LONGITUDE": False, "SALE PRICE": ":$,.0f", "size_m2": ":.0f", "YEAR BUILT": True}
    )

    color_scale = px.colors.sequential.GnBu
    df_quantiles = df_data[color_map].quantile(np.linspace(0, 1, len(color_scale))).to_frame()
    df_quantiles = round((df_quantiles - df_quantiles.min()) / (df_quantiles.max() - df_quantiles.min()) * 10000) / 10000
    df_quantiles.iloc[-1] = 1
    df_quantiles["colors"] = color_scale
    df_quantiles.set_index(color_map, inplace=True)
    
    color_scale = [[i, j] for i, j in df_quantiles["colors"].items()]

    map_fig.update_coloraxes(colorscale=color_scale)
    map_fig.update_layout(
        mapbox=dict(center=go.layout.mapbox.Center(lat=mean_lat, lon=mean_long), style="dark"), 
        template="plotly_dark", 
        paper_bgcolor="rgba(0, 0, 0, 0)", 
        margin=go.layout.Margin(l=0, r=0, t=0, b=0)
    )
    
    return hist_fig, map_fig, ts_fig, kpi_total_text, kpi_mean_text, kpi_median_text, kpi_m2_text

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050, debug=False)