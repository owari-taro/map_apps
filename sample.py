from dash import dash_table
from dash_extensions.enrich import DashProxy, Output, Input, State, html, dcc
import dash_leaflet as dl
import duckdb
from datetime import datetime, timedelta
import pandas as pd


def convert_bounds(extent: list):
    # extentの順序をleaflet用に入れ替える
    return [[float(extent[2]), float(extent[0])], [float(extent[3]), float(extent[1])]]


df = duckdb.sql("select * from 'images/meta/*.json'").df()
df["acq_date"] = pd.to_datetime(df["acq_date"])
records = df.to_dict("records")

# default_bounds = [[35.110165, 137.712216], [36.126243, 138.886210]]
default_bounds = convert_bounds(df.extent[0])
default_image = df.name[0]
default_url = (f"http://localhost:8080/thumbnail/{default_image}.jpg",)
app = DashProxy()
app.layout = html.Div(
    [
        dl.Map(
            id="map",
            children=[
                dl.ImageOverlay(
                    id="image",
                    url=f"http://localhost:8080/thumbnail/{default_image}.jpg",
                    bounds=default_bounds,
                    opacity=1,
                ),
                dl.TileLayer(
                    url="https://cyberjapandata.gsi.go.jp/xyz/english/{z}/{x}/{y}.png"
                ),
                dl.FeatureGroup(
                    [
                        dl.EditControl(
                            id="draw-control",
                            position="topright",
                            draw={
                                "rectangle": True,
                                "polygon": True,
                                "circle": False,
                                "circlemarker": False,
                                "marker": False,
                                "polyline": False,
                            },
                        )
                    ]
                ),
            ],
            bounds=default_bounds,
            style={"height": "60vh"},
        ),
        html.Div(
            [
                # City search
                html.Div(
                    [
                        html.Label(
                            "saerch by product name:",
                            style={"fontWeight": "bold", "marginRight": "10px"},
                        ),
                        dcc.Input(
                            id="search-box",
                            type="text",
                            placeholder="Type to search...",
                            style={"width": "200px", "padding": "5px"},
                        ),
                    ],
                    style={"marginBottom": "10px"},
                ),
                # Date range picker
                html.Div(
                    [
                        html.Label(
                            "Filter by Date:",
                            style={"fontWeight": "bold", "marginRight": "10px"},
                        ),
                        dcc.DatePickerRange(
                            id="date-picker",
                            min_date_allowed=datetime.now().date()
                            - timedelta(days=100),
                            max_date_allowed=datetime.now().date(),
                            initial_visible_month=datetime.now().date(),
                            start_date=datetime.now().date() - timedelta(days=2),
                            end_date=datetime.now().date(),
                            style={
                                "zIndex": 100
                            },  # Ensure calendar popup shows above map
                        ),
                    ]
                ),
            ],
            style={
                "margin": "10px 0",
                "padding": "10px",
                "backgroundColor": "#f8f9fa",
                "borderRadius": "5px",
            },
        ),
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
            style_table={"height": "300px", "overflowY": "auto"},
            style_cell={"textAlign": "left"},
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
            },
        ),
    ]
)


@app.callback(
    [Output("image", "url"), Output("image", "bounds"), Output("map", "bounds")],
    Input("table", "selected_rows"),
    State("store", "data"),
)  # mapのboundsは反応しないのでcenterで書き換える。
def update_image_bounds(selected_rows, store_data):
    if not selected_rows:
        url = f"http://localhost:8080/thumbnail/{default_image}.jpg"
        return (
            url,
            default_bounds,
            default_bounds,
        )
    row = store_data[selected_rows[0]]
    new_bounds = convert_bounds(row["extent"])
    url = f"http://localhost:8080/thumbnail/{row["name"]}.jpg"
    return url, new_bounds, new_bounds


@app.callback(
    [
        Output("table", "data"),
    ],
    [
        Input("search-box", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
    ],
    # State("store", "data"),
)
def select_table(search_term, start_date, end_date):
    from datetime import timezone

    filtered_df = df.copy()
    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )  # .date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )  # .date()
        filtered_df = filtered_df[
            (filtered_df["acq_date"] >= start_date)
            & (filtered_df["acq_date"] <= end_date)
        ]
    # Remove geometry column before returning data to the table
    if search_term:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(search_term, case=False, na=False)
        ]
    return filtered_df.drop("extent", axis=1).to_dict("records")
    # filtered_df.drop("geometry", axis=1).to_dict("records")


if __name__ == "__main__":
    app.run(debug=True)
