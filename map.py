import logging
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mapsplotlib import mapsplot as mplt

from plotter import pm_to_aqi_color

logger = logging.getLogger(__name__)


def scatter_map(
    lats,
    lons,
    values=None,
    colors=None,
    maptype="roadmap",
    alpha=0.5,
    fname="map.png",
    api_key=None,
):
    scale = 2
    max_size = 640  # Max size of the map in pixels
    width = scale * max_size
    colors = pd.Series(0, index=lats.index) if colors is None else colors
    map_data = "map_data.pkl"
    if api_key:
        logger.debug("Using Google Maps API key")
        mplt.register_api_key(api_key)
        img, pixels = mplt.background_and_pixels(lats, lons, max_size, maptype)
        with open(map_data, "wb") as f:
            pickle.dump([img, pixels], f)
            logger.debug("Saved map image and sensors pixels in {map_data}")
    else:
        with open(map_data, "rb") as f:
            img, pixels = pickle.load(f)
        logger.debug(f"Using local map data: {map_data}")
    plt.figure(figsize=(10, 10))
    plt.imshow(np.array(img))  # Background map
    plt.scatter(
        pixels["x_pixel"],
        pixels["y_pixel"],
        c=colors,
        s=width / 4,
        linewidth=0,
        alpha=alpha,
    )
    for index, row in pixels.iterrows():
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


def plot_scatter_map(sensors, fname="map.png", api_key=None):
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
