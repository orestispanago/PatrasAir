import json
import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)
dname = os.path.dirname(os.path.abspath(__file__))
sensor_names_file = os.path.join(dname, "sensor_names_gr.json")

with open(sensor_names_file, "r", encoding="utf8") as f:
    SENSOR_NAMES_GR = json.load(f)


def read_file(fname):
    df = pd.read_csv(fname, parse_dates=True, index_col="time_stamp")
    try:
        df.index = df.index.tz_convert("Europe/Athens")
    except AttributeError:
        logger.debug(f"Empty file: {fname}")
    return df


def get_last_record(df):
    try:
        last_dt = df.notna()[::-1].idxmax()["pm2.5"]
        last_value = df.loc[last_dt].values[0]
        return last_dt, last_value
    except ValueError:
        return None, None


class Sensor:
    def __init__(self, name="sensor", lat=38.26301, lon=21.74841):
        self.name = name
        self.lat = lat
        self.lon = lon

    def read(self, data_dir):
        self.data_24h = read_file(f"{data_dir}/{self.name}/24h_{self.name}.csv")
        self.data_7d = read_file(f"{data_dir}/{self.name}/7d_{self.name}.csv")
        self.last_dt, self.last_value = get_last_record(self.data_24h)


def read_sensors(sensors_csv, data_dir="data"):
    df = pd.read_csv(sensors_csv)
    logger.debug(f"Found {len(df)} sensors in {sensors_csv}")
    sensors = []
    for index, row in df.iterrows():
        sensor = Sensor(
            name=row["name"],
            lat=row["latitude"],
            lon=row["longitude"],
        )
        sensor.read(data_dir)
        sensors.append(sensor)
    logger.info(f"Read data for {len(sensors)} sensors")
    return sensors
