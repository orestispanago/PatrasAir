import fnmatch
import logging
import os
from datetime import datetime, timedelta
from io import StringIO

import numpy as np
import pandas as pd
import requests

logger = logging.getLogger(__name__)

READ_KEY = ""
SENSORS_FILE = "sensors.csv"
DATETIME_FORMAT = "%Y-%m-%dT%XZ"


def download_historical(sensor_id, start="", end="", average_minutes=0):
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
    resp = requests.get(url, headers={"x-api-key": READ_KEY})
    logger.debug(f"Sensor ID: {sensor_id}, Response status: {resp.status_code}")
    if resp.status_code != 200:
        logger.error(
            f"Response status not 200 for sensor ID: {sensor_id}\n"
            f"Response status: {resp.status_code}\n"
            f"Response text: \n {resp.text}"
        )
    data = StringIO(resp.text)
    df = pd.read_csv(data, parse_dates=True, index_col="time_stamp")
    logger.info(
        f"Retrieved {len(df)} records for sensor id: {sensor_id}, average: {average_minutes} minutes"
    )
    df.sort_index(inplace=True)
    return df


def nan_where_cf_less_than_atm(df, cf_cols, atm_cols):
    for cf_col, atm_col in zip(cf_cols, atm_cols):
        df[df[cf_col] < df[atm_col]] = np.nan


def nan_particle_order(df):
    # Implement QC based on pm1>pm2.5>pm10
    # sensor A
    df[df["pm1.0_cf_1_a"] > df["pm2.5_cf_1_a"]] = np.nan
    df[df["pm1.0_cf_1_a"] > df["pm10.0_cf_1_a"]] = np.nan
    df[df["pm2.5_cf_1_a"] > df["pm10.0_cf_1_a"]] = np.nan
    # sensor B
    df[df["pm1.0_cf_1_b"] > df["pm2.5_cf_1_b"]] = np.nan
    df[df["pm1.0_cf_1_b"] > df["pm10.0_cf_1_b"]] = np.nan
    df[df["pm2.5_cf_1_b"] > df["pm10.0_cf_1_b"]] = np.nan


def nan_where_negative(df, cf_cols):
    for cf_col in cf_cols:
        df[df[cf_col] < 0] = np.nan


def apply_calibration_factor(df):
    df["pm1.0_cf_1_a"] = df["pm1.0_cf_1_a"] * 0.52 - 0.18
    df["pm1.0_cf_1_b"] = df["pm1.0_cf_1_b"] * 0.52 - 0.18
    df["pm2.5_cf_1_a"] = df["pm2.5_cf_1_a"] * 0.42 + 0.26
    df["pm2.5_cf_1_b"] = df["pm2.5_cf_1_b"] * 0.42 + 0.26
    df["pm10.0_cf_1_a"] = df["pm10.0_cf_1_a"] * 0.45 + 0.02
    df["pm10.0_cf_1_b"] = df["pm10.0_cf_1_b"] * 0.45 + 0.02
    # Correct calibrated data when pm1<0
    df.loc[df["pm1.0_cf_1_a"] < 16, "pm1.0_cf_1_a"] = df["pm1.0_cf_1_a"] + 0.18
    df.loc[df["pm1.0_cf_1_b"] < 16, "pm1.0_cf_1_b"] = df["pm1.0_cf_1_b"] + 0.18


def quality_control(df):
    df_cols = list(df)
    cf_cols = fnmatch.filter(df_cols, "*cf*")
    atm_cols = fnmatch.filter(df_cols, "*atm*")
    nan_where_cf_less_than_atm(df, cf_cols, atm_cols)
    nan_particle_order(df)
    nan_where_negative(df, cf_cols)
    nan_particle_order(df)


def calc_pm25(df):
    df["pm2.5"] = df[["pm2.5_cf_1_a", "pm2.5_cf_1_b"]].mean(axis=1)
    ratio = abs(df["pm2.5_cf_1_a"] - df["pm2.5_cf_1_b"]) / df["pm2.5"]
    df["pm2.5"][ratio > 0.2] = np.nan


def correct_data(df):
    quality_control(df)
    apply_calibration_factor(df)
    calc_pm25(df)


def mkdir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.debug(f"Created local directory {dir_path}")


def save_pm25_csv(df, dir="data", sensor_name="", prefix=""):
    fpath = f"{dir}/{sensor_name}/{prefix}{sensor_name}.csv"
    mkdir_if_not_exists(os.path.dirname(fpath))
    df = df.filter(["pm2.5"])
    df.to_csv(fpath)
    logger.info(f"Wrote {len(df)} records to: {fpath}")


def download_qc_data(dir="data"):
    sensors = pd.read_csv(SENSORS_FILE)
    utc_now = pd.to_datetime(datetime.utcnow(), utc=True)
    yesterday = (utc_now - timedelta(days=1)).strftime(DATETIME_FORMAT)
    a_week_ago = (utc_now - timedelta(days=7)).strftime(DATETIME_FORMAT)
    end_date = utc_now.strftime(DATETIME_FORMAT)
    for index, row in sensors.iterrows():
        sensor_id = row["sensor_index"]
        sensor_name = row["name"]
        last_day = download_historical(sensor_id, start=yesterday, end=end_date)
        last_week = download_historical(
            sensor_id, start=a_week_ago, end=end_date, average_minutes=60
        )
        correct_data(last_day)
        correct_data(last_week)
        save_pm25_csv(last_day, dir=dir, sensor_name=sensor_name, prefix="24h_")
        save_pm25_csv(last_week, dir=dir, sensor_name=sensor_name, prefix="7d_")
    logger.info(f"Download successful")
