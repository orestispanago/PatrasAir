import logging

import pandas as pd

logger = logging.getLogger(__name__)


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
    def __init__(
        self, data_dir="data", name="sensor", lat=38.26301, lon=21.74841
    ):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.data_24h = read_file(f"{data_dir}/{self.name}/24h_{self.name}.csv")
        self.data_7d = read_file(f"{data_dir}/{self.name}/7d_{self.name}.csv")
        self.last_dt, self.last_value = get_last_record(self.data_24h)


def get_sensors(sensors_csv, data_dir="data"):
    df = pd.read_csv(sensors_csv)
    sensors = []
    for index, row in df.iterrows():
        sensor = Sensor(
            data_dir=data_dir,
            name=row["name"],
            lat=row["latitude"],
            lon=row["longitude"],
        )
        sensors.append(sensor)
    logger.info(f"Found {len(sensors)} sensors in {sensors_csv}")
    return sensors
