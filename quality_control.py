import fnmatch

import numpy as np


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


def clean(df):
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
    df.loc[ratio > 0.6, "pm2.5"] = np.nan


def quality_control(df):
    clean(df)
    apply_calibration_factor(df)
    calc_pm25(df)
    df.drop(columns=df.columns.difference(["pm2.5"]), inplace=True)
