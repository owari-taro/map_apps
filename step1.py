import dash_leaflet as dl
from dash_extensions.enrich import DashProxy
from dash import html, dash_table, Input, Output, State
import pandas as pd
from dash.exceptions import PreventUpdate

# Sample data
data = {
    'City': ['Tokyo', 'Osaka', 'Nagoya', 'Fukuoka'],
    'Latitude': [35.6762, 34.6937, 35.1814, 33.5902],
    'Longitude': [139.6503, 135.5023, 136.9064, 130.4017],
    'Population': ['37.4M', '19.1M', '9.4M', '5.5M']
}
df = pd.DataFrame(data)

app = DashProxy()
app.layout = html.Div([
    # Map component
    dl.Map([
        dl.TileLayer(url="https://cyberjapandata.gsi.go.jp/xyz/english/{z}/{x}/{y}.png"),
    ],
    id='map',
    center=[35.9009,137.3258], 
    zoom=5, 
    style={"height": "50vh"}),
    
    # Search box
    html.Div([
        html.Label("Search Cities:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.Input(
            id='search-box',
            type='text',
            placeholder='Type to search...',
            style={'width': '200px', 'marginBottom': '10px', 'padding': '5px'}
        ),
    ], style={'margin': '10px 0'}),
    
    # Table component
    dash_table.DataTable(
        id='city-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        row_selectable='single'  # Allow row selection
    )
])

# Callback to update map when a row is selected
@app.callback(
    [Output('map', 'center'),
     Output('map', 'zoom')],
    Input('city-table', 'selected_rows'),
    State('city-table', 'data')
)
def update_map(selected_rows, data):
    if not selected_rows:
        raise PreventUpdate
    
    # Get the selected city's coordinates
    selected_row = data[selected_rows[0]]
    print(selected_row)
    lat = selected_row['Latitude']
    lon = selected_row['Longitude']
    #35.68886,139.75381
    # Return new center and zoom level
    print(lat,lon)
    #zoom levelが大きすぎると地図が表示されない
    return [lat, lon], 10

if __name__ == "__main__":
    app.run()