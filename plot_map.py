import logging
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mapsplotlib import mapsplot as mplt
from mapsplotlib.google_static_maps_api import GoogleStaticMapsAPI

from plot_timeseries import pm_to_aqi_color
from config import GOOGLE_MAPS_API_KEY

logger = logging.getLogger(__name__)


def get_background(center_lat, center_lon, zoom, scale, max_size, api_key=None):
    map_background_file = "map_background.pickle"
    api_key = GOOGLE_MAPS_API_KEY
    if api_key:
        mplt.register_api_key(api_key)
        img = GoogleStaticMapsAPI.map(
            center=(center_lat, center_lon),
            zoom=zoom,
            scale=scale,
            size=(max_size, max_size),
            maptype="roadmap",
        )
        with open(map_background_file, "wb") as f:
            pickle.dump(img, f)
        logger.debug(f"Saved map background in {map_background_file}")
        return img
    logger.debug(f"Using local map data: {map_background_file}")
    with open(map_background_file, "rb") as f:
        img = pickle.load(f)
    return img


def calc_map_params(lats, lons):
    scale = 2
    max_size = 580  # Max size of the map in pixels
    width = scale * max_size
    center_lat = (lats.max() + lats.min()) / 2
    center_lon = (lons.max() + lons.min()) / 2
    zoom = GoogleStaticMapsAPI.get_zoom(lats, lons, max_size, scale)
    return scale, max_size, width, center_lat, center_lon, zoom


def scatter_map(
    lats,
    lons,
    values=None,
    colors=None,
    alpha=0.5,
    fname="map.jpg",
    api_key=None,
):
    scale, max_size, width, center_lat, center_lon, zoom = calc_map_params(
        lats, lons
    )
    img = get_background(
        center_lat, center_lon, zoom, scale, max_size, api_key=api_key
    )
    sensor_pixels = GoogleStaticMapsAPI.to_tile_coordinates(
        lats, lons, center_lat, center_lon, zoom, max_size, scale
    )
    plt.figure(figsize=(7.5, 7.5))
    plt.imshow(np.array(img))  # Background map
    plt.scatter(
        sensor_pixels["x_pixel"],
        sensor_pixels["y_pixel"],
        c=colors,
        s=width / 4,
        linewidth=0,
        alpha=alpha,
    )
    for index, row in sensor_pixels.iterrows():
        plt.text(
            row["x_pixel"],
            row["y_pixel"],
            int(values[index]),
            horizontalalignment="center",
            verticalalignment="center",
            weight="bold",
        )
    plt.gca().invert_yaxis()  # Origin of map is upper left
    plt.axis([0, width, width, 0])  # Remove margin
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(fname)
    logger.info(f"Plotted {len(values)} points on map")


def prepare_map_data(sensors):
    df = pd.DataFrame(columns=["name", "lat", "lon", "last_value"])
    for count, sensor in enumerate(sensors):
        df.loc[count] = [sensor.name, sensor.lat, sensor.lon, sensor.last_value]
    df = df.dropna()
    df["color"] = df["last_value"].apply(pm_to_aqi_color)
    return df


def plot_scatter_map(sensors, fname="map.jpg", api_key=None):
    df = prepare_map_data(sensors)
    scatter_map(
        df["lat"],
        df["lon"],
        values=df["last_value"],
        colors=df["color"],
        alpha=1,
        fname=fname,
        api_key=api_key,
    )
