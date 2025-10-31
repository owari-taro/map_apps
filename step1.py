import dash_leaflet as dl
from dash_extensions.enrich import DashProxy, html
from dash import dash_table, Input, Output, State, dcc
import pandas as pd
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta
from shapely.geometry import Point, Polygon
import json

# Sample data with dates
data = {
    'City': ['Tokyo', 'Osaka', 'Nagoya', 'Fukuoka'] * 3,  # Repeat cities for different dates
    'Latitude': [35.6762, 34.6937, 35.1814, 33.5902] * 3,
    'Longitude': [139.6503, 135.5023, 136.9064, 130.4017] * 3,
    'Population': ['37.4M', '19.1M', '9.4M', '5.5M'] * 3,
    'Date': [
        # Today and previous days for each city
        *[datetime.now().date() for _ in range(4)],
        *[(datetime.now() - timedelta(days=1)).date() for _ in range(4)],
        *[(datetime.now() - timedelta(days=2)).date() for _ in range(4)]
    ]
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
    
    # Search and filter controls
    html.Div([
        # City search
        html.Div([
            html.Label("Search Cities:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Input(
                id='search-box',
                type='text',
                placeholder='Type to search...',
                style={'width': '200px', 'padding': '5px'}
            ),
        ], style={'marginBottom': '10px'}),
        
        # Date range picker
        html.Div([
            html.Label("Filter by Date:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=datetime.now().date() - timedelta(days=2),
                max_date_allowed=datetime.now().date(),
                initial_visible_month=datetime.now().date(),
                start_date=datetime.now().date() - timedelta(days=2),
                end_date=datetime.now().date(),
                style={'zIndex': 100}  # Ensure calendar popup shows above map
            ),
        ]),
    ], style={'margin': '10px 0', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),
    
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

# Callback to filter table based on search input and date range
@app.callback(
    Output('city-table', 'data'),
    [Input('search-box', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_table(search_term, start_date, end_date):
    filtered_df = df.copy()
    
    # Filter by date range
    if start_date and end_date:
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
        filtered_df = filtered_df[
            (filtered_df['Date'] >= start_date) & 
            (filtered_df['Date'] <= end_date)
        ]
    
    # Filter by city name
    if search_term:
        filtered_df = filtered_df[
            filtered_df['City'].str.contains(search_term, case=False, na=False)
        ]
    
    return filtered_df.to_dict('records')

if __name__ == "__main__":
    app.run()