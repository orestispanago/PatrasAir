import pandas as pd
import requests

from config import GOOGLE_MAPS_API_KEY

center = "Patras"
zoom = 12
size = "750x600"

sensors = pd.read_csv("sensors.csv")
coords = []
for index, row in sensors.iterrows():
    sensor_lat = row["latitude"]
    sensor_lon = row["longitude"]
    coords.append(f"{sensor_lat},{sensor_lon}%7C")
marker_coords = "".join(coords)


url = (
    f"https://maps.googleapis.com/maps/api/staticmap?"
    f"center={center}&"
    f"zoom={zoom}&"
    f"size={size}&"
    f"markers={marker_coords}&"
    f"key={GOOGLE_MAPS_API_KEY}"
)
r = requests.get(url)
print(r.status_code)

with open("map.png", "wb") as f:
    f.write(r.content)
