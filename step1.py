import dash_leaflet as dl
from dash_extensions.enrich import DashProxy
from dash import html, dash_table
import pandas as pd

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
    dl.Map(dl.TileLayer(url="https://cyberjapandata.gsi.go.jp/xyz/english/{z}/{x}/{y}.png"),
           center=[35.9009,137.3258], zoom=5, style={"height": "50vh"}),
    
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
        }
    )
])

if __name__ == "__main__":
    app.run()