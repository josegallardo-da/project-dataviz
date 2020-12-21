import pydeck as pdk
import pandas as pd

from palettable.cartocolors.sequential import Peach_2

def mx_map(mx_trade, period='Sep-2020'):

    # Countries to Use

    countries_df = list(mx_trade['Partner'].unique())
    countries_df = countries_df[1:len(countries_df)-1]

    countries = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSNVgKbD5eXrt-3shmAKShYA_PPQmgep-b04UQMmiYtpYTmDLfOgfmbKBtTPB3zR6NnyA6MIf3QGvW_/pub?output=csv')
    countries['name'] = countries['name'].replace('United States', 'USA')
    countries = countries.sort_values(by=['name'], ignore_index = True)

    difference = set(countries_df) - set(list(countries['name']))
    difference = list(set(difference))

    for d in difference:
        countries_df.remove(d)

    data_map = mx_trade.query(f'Partner == {countries_df}').sort_values(by='Partner', ascending=True)

    lat = [countries.loc[countries['name'] == p, 'latitude'].item() for p in list(data_map['Partner'])]
    lon = [countries.loc[countries['name'] == p, 'longitude'].item() for p in list(data_map['Partner'])]

    data_map['Latitude'] = lat
    data_map['Longitude'] = lon 

    data_map = data_map.sort_values(by='Period', ascending=True)

    data_map_viz = data_map.query('Period == "2005" and Regimen == "Exports"')
    data_map_viz = data_map_viz.rename(columns={'Trade Value': 'TradeValue', 'Latitude':'latitude', 'Longitude':'longitude'})

    mapbx_api = 'pk.eyJ1Ijoiam9zZS1neiIsImEiOiJja2l2M3B4ZGswZ21iMnNwZ283Y2lvdjlwIn0.Bp8yEEwlAR9ZDLzpwzOtxw'

    # data
    map_viz = data_map_viz

    # view (location, zoom level, etc.)
    view = pdk.ViewState(latitude=23.634501, longitude=-102.552784, pitch=25, zoom=4)

    # layer
    heatmap_layer = pdk.Layer('HeatmapLayer',
                            data=map_viz,
                            opacity=0.9,
                            get_position=["longitude", "latitude"],
                            color_range= Peach_2.colors,
                            threshold=0.1, #cell_size_pixels=50,
                            get_weight= 'TradeValue',
                            pickable=True)

    # render map
    heatmap_layer_map = pdk.Deck(layers=heatmap_layer, 
                                initial_view_state=view,
                                mapbox_key=mapbx_api)

    # display and save map (to_html(), show())
    return heatmap_layer_map