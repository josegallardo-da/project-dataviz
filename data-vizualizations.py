
# Getting all the libraries 

from os import getcwd

# -- The Following tww codes correspond to the other two files found in this table ...
from extracting_uncomtrade import *
from mapmx import *

# -- Libraries to use for data manipulation, cleaning and visualization ...
from random import sample, choice
import pandas as pd
import plotly.graph_objects as go
import matplotlib.colors as cl
import plotly.express as px

# -- Dash Libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
from dash.dependencies import Input, Output
import dash_deck

# -- To protect our personal MAPBOX API TOKEN
from pyautogui import password

# Getting & Saving the Data (Only for Updating the Data)

"""
mx_trade = data_prettifier(data_extraction())
mx_trade.to_json(f'{getcwd()}\\mexico-trade-data.json', orient='records')
"""

# Having the data as a json file, we are going to keep as a comment the code above ...

# -- Using Pandas to read data
mx_trade = pd.read_json('mexico-trade-data.json', orient='records')

# -- Preparing Data for Vizualizations
mx_trade = mx_trade.sort_values(by=['Period'], ignore_index = True)
mx_trade = time_period(mx_trade)
mx_trade.Period = mx_trade.Period.apply(lambda t: t.strftime('%Y') if t.year in range(1990,2010) else t.strftime('%b-%Y'))
mx_trade['Regimen'] = mx_trade['Regimen'].replace(['Import','Export'], ['Imports', 'Exports'])
mx_trade['Partner'] = mx_trade['Partner'].replace('United States of America', 'USA')

# -- Defining the elements for the Components, which are going to be Dropdowns that are going to filter our Data

periods_str = list(mx_trade['Period'].unique()) # time periods of our data
options_dd = [{'label': period, 'value':period} for period in periods_str] # dict of periods_str to use on the Dash Component

# MAP

# -- You'll need a API Token to display the map, visit MAPBOX to create an account ...
# --  Inputting mapbox's api token
mapbx_api = password(text = 'MAPBOX API TOKEN', title = 'MAPBOX API TOKEN', mask = '*')

# -- Creating the Map through mx_map which is a function from another py.file
mx = mx_map(mx_trade)
# -- Dash_Deck is needed here to insert the map in our Dash App's Layout
deck_component = dash_deck.DeckGL(mx.to_json(), id="deck-gl", mapboxKey=mapbx_api)

# Preparing the Visualizations' Attributes

# -- Get colors from: https://hihayk.github.io/scale/#128/128/0/99/-360/360/100/100/1D9A6C/29/154/108/black
colors = '''#FF00FF #FF00FF #FF00FF #FF00C5 #FF008B #FF0051 #FF0019 #FF0000 #FF0000 #FF0000 #FF0000 #FF3000 #FF6600 #FF9B00 #FFCF00 #FFFF00 #FFFF00 #FFFF00 #FFFF00
#DBFF00 #A9FF00 #79FF00 #4AFF00 #1CFF00 #00FF00 #00FF00 #00FF00 #00FF21 #00FF4E #00FF7A #00FFA4 #00FFCE #00FFF6 #00FFFF #00FFFF #00E3FF #00BBFF #0094FF #006EFF
#004AFF #0026FF #0004FF #0000FF #1F00FF #4300FF #6500FF #8600FF #A600FF #C500FF #E301FF #FF03FF #E306FF #C70AFF #AC0FFF #9014FF #7519FF #591EFF #3E23FF #2828FF
#2D31FF #3351FF #3871FF #3D91FF #42B0FF #47CEFF #4CECFF #51FFFF #56FFFF #5BFFF9 #60FFE0 #65FFC8 #6AFFB1 #6FFF9B #74FF86 #79FF79 #7EFF7E #83FF83 #95FF88 #AEFF8D
#C6FF92 #DCFF98 #F1FF9D #FFFFA2 #FFFFA7 #FFFFAC #FFFFB1 #FFF1B6 #FFE4BB #FFD9C0 #FFD0C5 #FFCACA #FFCFCF #FFD4D4 #FFD9D9 #FFDEE1 #FFE3EC #FFE8F5 #FFEDFB #FFF2FF 
#FFF7FF #FFFCFF'''
colors = list(set(colors.split())) # create a list of the colors to employ

# Initiating DASH App
# -- BS refers to CSS stylesheet that we're going to use to facilitate the design process of our App's Layout
BS = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/cyborg/bootstrap.min.css"
app = dash.Dash(__name__, external_stylesheets=[BS])

# Dash App Layout

# -- Defining the colors for our app

app_colors = {
    'background': '#131314',
    'bg_div': '#000000',
    'text': '#FFFFFF'
}

# -- Defining the structure ... how our app is going to look like?

intro = html.Div(dbc.Row(dbc.Col(html.Div(children=deck_component)))) 

app.layout = html.Div(children=[
    html.Div(intro), # the map but it remains as a background --> need to be checked to correct
    
    html.Div([
    dcc.Dropdown( # this is the button that is going to allow the user to filter the data by Time Period

        id = 'dropdown_periods', # establish a unique id, to refer this button when doing our callbacks.
        options = options_dd, # this is a dictionary with the labels and values, this was created from our Dataframe
        value = ['Sep-2020'], # this is the default value
        multi = True, # allows multiple options to be inputted
        searchable = True), # allows the user to search for the options by typing them

    # The following are the graphs, it is important to establish an id for each one of them, since this is going to establish the app's callbacks
    dcc.Graph(id = 'sankey_mxtrade'), 
    html.Br(), # space between graphs
    dcc.Graph(id = 'distribution_pimp'),
    html.Br(),
    dcc.Graph(id = 'distribution_pexp'),
    html.Br(),
    dcc.Graph(id = 'lines_imp')])
    #html.Br(),
    #dcc.Graph(id = 'lines_exp')
    ], style={'backgroundColor': app_colors['background'], 'overflowY': 'scroll', 'height': 500})
                                                            # without this, we would not be able to scroll through our web app

# Connect the Plotly graphs with Dash Components

# -- Each one of the outputs correspond to each Graph that we previously established in our layout, as you can see from the ids stated below
# -- 1 USER INPUT --> 3 OUTPUTS, 1 OUTPUT MORE THAT ISN'T AFFECTED BY THE USER'S INPUT
@app.callback(
    [Output(component_id='sankey_mxtrade', component_property='figure'), 
    Output(component_id='distribution_pimp', component_property='figure'),
    Output(component_id='distribution_pexp', component_property='figure'),
    Output(component_id='lines_imp', component_property='figure')#,
    #Output(component_id='lines_exp', component_property='figure')
    ],
    [Input(component_id='dropdown_periods', component_property='value')] # this id corresponds to the one from our dropdown button
    )

# Creating the Graphs

# -- To display our inputs and outputs, a function that returns the graphs or figures needs to be created ...
def update_graph(period): # the arguments received by the function, are going to be the User's inputs
    
    data = mx_trade.copy()
    # Using the user's input to filter the data through pandas query ...
    data_toviz = data.query(f'Period == {period}')

    if len(period) == 1:

        imports = data_toviz[data_toviz['Regimen'] == 'Imports'].sort_values(by='Trade Value', ascending=False).head(20)
        exports = data_toviz[data_toviz['Regimen'] == 'Exports'].sort_values(by='Trade Value', ascending=False).head(20)
    
    # if the User's input refers to more than one time period, the data is going to be grouped by all the Time Periods, using the sum agg function.
    if len(period) > 1:

        imports = data_toviz[data_toviz['Regimen'] == 'Imports'].groupby(['Partner'], as_index = False).agg({'Trade Value':'sum'}).sort_values(by='Trade Value', ascending=False).head(50)
        exports = data_toviz[data_toviz['Regimen'] == 'Exports'].groupby(['Partner'], as_index = False).agg({'Trade Value':'sum'}).sort_values(by='Trade Value', ascending=False).head(50)

    # When no User's input is received, the data is going to be groupby by all the time periods that are available, using the sum agg function.
    if len(period) == 0:

        imports = data[data['Regimen'] == 'Imports'].groupby(['Partner'], as_index = False).agg({'Trade Value':'sum'}).sort_values(by='Trade Value', ascending=False).head(50)
        exports = data[data['Regimen'] == 'Exports'].groupby(['Partner'], as_index = False).agg({'Trade Value':'sum'}).sort_values(by='Trade Value', ascending=False).head(50)

    # SANKEY GRAPH
    # -- Getting the Labels, which are the names of the countries.
    imp_labels = list(imports['Partner'])
    exp_labels = list(exports['Partner'])

    # -- The Labels that are going to appear to represent the Nodes
    labels = ['Mexico']
    labels.extend(imp_labels)
    labels.extend(exp_labels)
    
    # -- This list of labels, is to define a color for each of the Countries appearing in our graph 
    lb_lst = list(set(labels))

    # -- Color Attributes for Sankey Graph

    # -- Selecting the colors to be used
    colors_rd = sample(colors, len(colors)) # alt --> colors_ctry = {c:choice(colors) for c in country_lst}

    colors_nodes = [cl.to_rgba(c, alpha=1) for c in colors_rd]
    colors_nodes = [f'rgba{c}' for c in colors_nodes]
    colors_nodes = {lb_lst[i] : colors_nodes[i] for i in range(len(lb_lst))}

    colors_links = [cl.to_rgba(c, alpha=0.5) for c in colors_rd]
    colors_links = [f'rgba{c}' for c in colors_links]
    colors_links = {lb_lst[i] : colors_links[i] for i in range(len(lb_lst))}

    # -- Fixed Colors
    colors_nodes['World'] = 'rgba(241, 130, 141, 1)' 
    colors_nodes['USA'] = 'rgba(83, 51, 237, 1)' 
    colors_nodes['Mexico'] = 'rgba(255,255,255, 1)'

    colors_links['World'] = 'rgba(241, 130, 141,0.5)' 
    colors_links['USA'] = 'rgba(83, 51, 237,0.5)' 

    # -- Final List of Colors
    n_colors = [colors_nodes[label] for label in labels[:len(labels)]]
    lk_colors = [colors_links[label] for label in labels[:len(labels)]][1:len(labels)]

    # -- Establishing the links between the data
    source = list(range(len(labels)))[1:len(imp_labels)+1] + [0]*len(imp_labels)
    target = [0]*len(imp_labels) + list(range(len(labels)))[len(imp_labels)+1:len(labels)]
    value = list(imports['Trade Value']) + list(exports['Trade Value'])

    # -- Links Dictionary
    link = dict(source = source, target = target, value = value, color = lk_colors)

    fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad = 50,
        thickness = 15,
        line = dict(color = "white", width = 0),
        label = labels,
        color = n_colors),
        link = link)
        ])

    # -- Adding more details to the sankey-graph
    fig.update_layout(title_text="MX ¿Cuanto Compramos & Cuanto Vendemos?", title_font_color="white", font_size=12, paper_bgcolor='black')

    # Enriching the Dash App with more Visualizations with Plotly Express
    
    # -- Pie Chart for Imports
    pie_imp = px.pie(imports, values='Trade Value', names='Partner', title='La Huella Global en Mexico', template="plotly_dark")
    pie_imp.update_traces(textposition='outside', textinfo='percent+label')
    
    # -- Pie Chart for Exports
    pie_exp = px.pie(exports, values='Trade Value', names='Partner', title='La Huella de Mexico en el Mundo', template="plotly_dark")
    pie_exp.update_traces(textposition='outside', textinfo='percent+label')

    # --  Line Graph for Imports ## Error displayed with the Exports data ...
    mx_imp = data.query('Regimen == "Imports"')
    #mx_exp = data.query('Regimen == "Exports"')

    lines_i = px.line(mx_imp, x="Period", y="Trade Value", color="Partner", template="plotly_dark")
    #lines_e = px.line(mx_exp, x="Period", y="Trade Value", color="Partner")

    return [fig, pie_imp, pie_exp, lines_i] # list of all the Figures or Graphs that are expected to be Visualized

# Run the App

if __name__ == '__main__':
    app.run_server(debug=True)
