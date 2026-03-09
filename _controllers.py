from dash import html, dcc
import dash_bootstrap_components as dbc
from app import app

list_of_locations = {
    "All": 0,
    "Manhattan": 1,
    "Bronx": 2,
    "Brooklyn": 3,
    "Queens": 4,
    "Staten Island ": 5,
}

slider_size = [100, 500, 1000, 10000, 10000000]

controllers = dbc.Row([
    dcc.Store(id='store-global'),
    
    # ==========================================
    # NOVA LOGO ESTILO SITE VISION DATA PRÓ
    # ==========================================
    html.Div([
        html.Span("VISIO", style={"fontFamily": "Oswald, sans-serif", "fontWeight": "bold", "color": "white", "fontSize": "28px"}),
        html.Span("DATA", style={"fontFamily": "Oswald, sans-serif", "fontWeight": "300", "color": "#d1d5db", "fontSize": "28px", "marginLeft": "2px", "marginRight": "6px"}),
        html.Span("PRÓ", style={
            "backgroundColor": "rgba(234, 88, 12, 0.2)",
            "border": "1px solid rgba(249, 115, 22, 0.3)",
            "color": "#fb923c",
            "fontSize": "11px",
            "fontWeight": "bold",
            "padding": "3px 6px",
            "borderRadius": "4px",
            "letterSpacing": "1px",
            "position": "relative",
            "top": "-4px" 
        })
    ], style={"display": "flex", "alignItems": "center", "marginBottom": "30px", "marginTop": "10px"}),
    
    # Textos da Vision Pró Data
    html.H3("Análise Imobiliária - NYC", style={"margin-top": "20px"}),
    html.P("Desenvolvido por Vision Pró Data", style={"font-weight": "bold", "color": "#e08b1b"}), 
    html.P(
        "Explore a distribuição e precificação de imóveis em Nova York utilizando dados históricos. Filtre por região e tamanho para insights detalhados."
    ),

    html.H4("Borough", style={"margin-top": "40px", "margin-bottom": "20px"}),
    dcc.Dropdown(
        id="location-dropdown",
        options=[{"label": i, "value": j} for i, j in list_of_locations.items()],
        value=0,
        placeholder="Selecione a região",
        style={"color": "#000000"} 
    ),

    html.P("Metragem (m2)", style={"margin-top": "20px"}),

    dcc.Slider(
        min=0, max=4, id='slider-square-size', value=4,
        marks={i: str(j) for i, j in enumerate(slider_size)}
    ),

    html.P("Variável de análise", style={"margin-top": "20px"}),
    
    dcc.Dropdown(
        options=[
            {'label': 'Ano de Construção', 'value': 'YEAR BUILT'},
            {'label': 'Total de Unidades', 'value': 'TOTAL UNITS'},
            {'label': 'Preço de Venda', 'value': 'SALE PRICE'},
        ],
        value='SALE PRICE',
        id="dropdown-color",
        style={"color": "#000000"}
    )
])