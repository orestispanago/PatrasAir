import logging
import os
from datetime import datetime, timedelta
from io import StringIO

import pandas as pd
import requests

from config import READ_KEY
from quality_control import quality_control
from utils import mkdir_if_not_exists

logger = logging.getLogger(__name__)


def get_sensor_history_csv(
    sensor_id, start, end, average_minutes=0, read_key=READ_KEY
):
    url = (
        f"https://api.purpleair.com/v1/sensors/{sensor_id}/history/csv?"
        f"start_timestamp={start}&"
        f"end_timestamp={end}&"
        f"average={average_minutes}&"
        f"fields=pm1.0_cf_1_a,"
        f"pm1.0_cf_1_b,"
        f"pm2.5_cf_1_a,"
        f"pm2.5_cf_1_b,"
        f"pm10.0_cf_1_a,"
        f"pm10.0_cf_1_b,"
        f"pm1.0_atm_a,"
        f"pm1.0_atm_b,"
        f"pm2.5_atm_a,"
        f"pm2.5_atm_b,"
        f"pm10.0_atm_a,"
        f"pm10.0_atm_b,"
    )
    resp = requests.get(url, headers={"x-api-key": read_key})
    logger.debug(f"Sensor ID: {sensor_id}, Response status: {resp.status_code}")
    if resp.status_code != 200:
        logger.warning(
            f"Response status not 200 for sensor ID: {sensor_id}\n"
            f"Response status: {resp.status_code}\n"
            f"Response text: \n {resp.text}"
        )
    return resp


def read_response(resp):
    data = StringIO(resp.text)
    df = pd.read_csv(data, parse_dates=True, index_col="time_stamp")
    df.sort_index(inplace=True)
    return df


def save_as_csv(df, dir, sensor_name, prefix="prefix_"):
    fpath = f"{dir}/{sensor_name}/{prefix}{sensor_name}.csv"
    mkdir_if_not_exists(os.path.dirname(fpath))
    df.to_csv(fpath)
    logger.debug(f"Wrote {len(df)} records to: {fpath}")


def download_csv(
    sensor_id, dir, start, end, sensor_name, prefix, average_minutes=0
):
    resp = get_sensor_history_csv(sensor_id, start, end, average_minutes)
    if resp.status_code == 200:
        df = read_response(resp)
        quality_control(df)
        save_as_csv(df, dir, sensor_name, prefix)
    else:
        logger.warning(f"Skipped download for sensor ID: {sensor_id}")


def download_sensors_data(sensors_csv="sensors.csv", dir="data", week=True):
    sensors = pd.read_csv(sensors_csv)
    utc_now = pd.to_datetime(datetime.utcnow(), utc=True)
    datetime_format = "%Y-%m-%dT%XZ"
    yesterday = (utc_now - timedelta(days=1)).strftime(datetime_format)
    a_week_ago = (utc_now - timedelta(days=7)).strftime(datetime_format)
    now = utc_now.strftime(datetime_format)
    for index, row in sensors.iterrows():
        sensor_id = row["sensor_index"]
        sensor_name = row["name"]
        download_csv(sensor_id, dir, yesterday, now, sensor_name, prefix="24h_")
        if week:
            download_csv(
                sensor_id,
                dir,
                a_week_ago,
                now,
                sensor_name,
                average_minutes=60,
                prefix="7d_",
            )
    logger.info(f"Downloaded data for {len(sensors)} sensors")
