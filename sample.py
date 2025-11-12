from dash import dash_table
from dash_extensions.enrich import DashProxy, Output, Input, State, html, dcc
import dash_leaflet as dl
import duckdb


def convert_bounds(extent: list):
    # extentの順序をleaflet用に入れ替える
    return [[float(extent[2]), float(extent[0])], [float(extent[3]), float(extent[1])]]


df = duckdb.sql("select * from 'images/meta/*.json'").df()
records = df.to_dict("records")

# default_bounds = [[35.110165, 137.712216], [36.126243, 138.886210]]
default_bounds = convert_bounds(df.extent[0])
default_image = df.name[0]

app = DashProxy()
app.layout = html.Div(
    [
        # store the full dataset (not shown)
        dcc.Store(id="store", data=records),
        # table only shows the name column to the user
        dash_table.DataTable(
            id="table",
            columns=[
                {"name": i, "id": i} for i in df[["name", "acq_date"]].columns
            ],  # [{"name": "Name", "acq_date": "acq_date", "id": "name"}],
            data=df[["name", "acq_date"]].to_dict("records"),  # full_data,
            row_selectable="single",
            selected_rows=[0],
        ),
        dl.Map(
            id="map",
            children=[
                dl.ImageOverlay(
                    id="image",
                    url=f"http://localhost:8080/thumbnail/{default_image}.jpg",
                    bounds=default_bounds,
                    opacity=1,
                ),
                dl.TileLayer(),
            ],
            bounds=default_bounds,
            style={"height": "60vh"},
        ),
    ]
)


@app.callback(
    Output("image", "bounds"),
    Output("map", "bounds"),
    Input("table", "selected_rows"),
    State("store", "data"),
)
def update_image_bounds(selected_rows, store_data):
    if not selected_rows:
        return default_bounds, default_bounds
    row = store_data[selected_rows[0]]
    new_bounds = convert_bounds(row["extent"])
    return new_bounds, new_bounds


if __name__ == "__main__":
    app.run(debug=True)
