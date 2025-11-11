import dash_leaflet as dl
from dash_extensions.enrich import DashProxy
'''
xmin (lon): 137.70836832265692
  ymin (lat): 35.11016547665246
  xmax (lon): 138.88621042735062
  ymax (lat): 36.12624261158598

'''
image_bounds = [[ 35.110165,137.712216,], [ 36.12624261158598,138.88621042735062]]
app = DashProxy()
app.layout = dl.Map(
    [dl.ImageOverlay(opacity=0.8, url="http://localhost:8080/thumbnail.jp2", bounds=image_bounds), dl.TileLayer()],
    bounds=image_bounds,
    style={"height": "50vh"},
)

if __name__ == "__main__":
    app.run()