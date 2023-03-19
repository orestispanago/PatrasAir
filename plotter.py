import glob
import locale
import logging
import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from utils import STATION_NAMES_GR, mkdir_if_not_exists

logger = logging.getLogger(__name__)

LARGE_FONT = 28
MEDIUM_FONT = 14

LIGHT_BLUE = "#43dbff"
GREEN = "#96cd4f"
YELLOW = "#ffff00"
RED = "#fc3903"
DARK_RED = "#990100"


def get_station_name(file):
    base_name = os.path.basename(file)[:-4]
    time_range, name = base_name.split("_")
    return name


def yaxis_color_aqi(ax):
    ymin, ymax = ax.get_ylim()
    ax.margins(y=0)
    if ymax >= 50:
        ax.axhspan(0, 10, color=LIGHT_BLUE)
        ax.axhspan(10, 20, color=GREEN)
        ax.axhspan(20, 25, color=YELLOW)
        ax.axhspan(25, 50, color=RED)
        ax.axhspan(50, ymax, color=DARK_RED)
    elif 25 <= ymax < 50:
        ax.axhspan(0, 10, color=LIGHT_BLUE)
        ax.axhspan(10, 20, color=GREEN)
        ax.axhspan(20, 25, color=YELLOW)
        ax.axhspan(25, 50, color=RED)
    elif 20 <= ymax < 25:
        ax.axhspan(0, 10, color=LIGHT_BLUE)
        ax.axhspan(10, 20, color=GREEN)
        ax.axhspan(20, 25, color=YELLOW)
    elif 10 <= ymax < 20:
        ax.axhspan(0, 10, color=LIGHT_BLUE)
        ax.axhspan(10, 20, color=GREEN)
    elif 0 <= ymax < 10:
        ax.axhspan(0, 10, color=LIGHT_BLUE)


def format_date(df, ax):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    if df.index[-1] - df.index[0] <= pd.Timedelta(days=1):
        fmt_date = mdates.DayLocator()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        sec_xaxis = ax.secondary_xaxis(-0.08)
        sec_xaxis.xaxis.set_major_locator(fmt_date)
        sec_xaxis.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        sec_xaxis.spines["bottom"].set_visible(False)
        sec_xaxis.tick_params(bottom=False)


def add_logos(
    ax, station_name="station A", img_path="img/lapup_aether_logos.png"
):
    pic = plt.imread(img_path)
    ax.imshow(pic)
    ax.text(
        500,
        -200,
        station_name,
        fontsize=MEDIUM_FONT,
        weight="bold",
        ha="center",
        va="center",
    )
    ax.axis("off")


def pm_to_aqi_color(pm_value):
    if type(pm_value) is str:
        return LIGHT_BLUE
    if pm_value < 10:
        return LIGHT_BLUE
    elif 10 <= pm_value < 20:
        return GREEN
    elif 20 <= pm_value < 25:
        return YELLOW
    elif 25 <= pm_value < 50:
        return RED
    elif pm_value >= 50:
        return DARK_RED


def show_no_data(ax):
    ax.text(
        0.5,
        0.5,
        "No Data",
        fontsize=LARGE_FONT,
        weight="bold",
        ha="center",
        va="center",
    )
    ax.axis("off")


def add_last_value(df, ax):
    if df.count().values[0] == 0:
        show_no_data(ax)
    else:
        last_dt = df.notna()[::-1].idxmax()
        last_pm_measurement = df.loc[last_dt]
        try:
            last_pm_value = int(last_pm_measurement["pm2.5"])
        except ValueError as e:
            last_pm_value = "No Data"
        last_dt_fmt = last_dt["pm2.5"].strftime("%d %b %H:%M")
        ax.set_facecolor(pm_to_aqi_color(last_pm_value))
        center_text = f"{last_pm_value} $\mu g/m^3$"
        ax.text(
            0.5,
            0.5,
            center_text,
            fontsize=LARGE_FONT,
            weight="bold",
            ha="center",
            va="center",
        )
        ax.text(
            0.5,
            0.9,
            last_dt_fmt,
            fontsize=MEDIUM_FONT,
            weight="bold",
            ha="center",
            va="center",
        )
        for axis in ["top", "bottom", "left", "right"]:
            ax.spines[axis].set_linewidth(2)
        ax.set_xticks([])
        ax.set_yticks([])


def plot_timeseries(df, ax):
    if df.count().values[0] <= 1:
        show_no_data(ax)
    else:
        ax.plot(df.index, df["pm2.5"], color="black", linewidth=2, markersize=2)
        yaxis_color_aqi(ax)
        format_date(df, ax)


def plot_station(df_7d, df_24h, name="station_a", folder="plots"):
    fig, axes = plt.subplots(
        2, 2, figsize=(10, 7), gridspec_kw={"width_ratios": [1, 2]}
    )
    ax_top_left = axes[0][0]
    ax_top_right = axes[0][1]
    ax_lower_left = axes[1][0]
    ax_lower_right = axes[1][1]

    plot_timeseries(df_24h, ax_top_right)
    plot_timeseries(df_7d, ax_lower_right)
    add_logos(ax_lower_left, station_name=STATION_NAMES_GR.get(name))
    add_last_value(df_24h, ax_top_left)
    fig.subplots_adjust(hspace=0.3)
    mkdir_if_not_exists(folder)
    plt.savefig(f"{folder}/{name}.png")
    plt.close()
    # plt.show()
    logger.debug(f"Plotted {name} ")


def read_file(fname):
    df = pd.read_csv(fname, parse_dates=True, index_col="time_stamp")
    try:
        df.index = df.index.tz_convert("Europe/Athens")
    except AttributeError:
        logger.debug(f"Empty file: {fname}")
    return df


def plot_stations(folder="plots"):
    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
    logger.debug(f"Set locale: {locale.getlocale(locale.LC_ALL)}")

    files_24h = glob.glob("*/*/24h*.csv")
    files_7d = glob.glob("*/*/7d*.csv")
    for file_24h, file_7d in zip(files_24h, files_7d):
        df_24h = read_file(file_24h)
        name = get_station_name(file_24h)
        df_7d = read_file(file_7d)
        plot_station(df_7d, df_24h, name=name, folder=folder)
    logger.info(f"Plotted {len(files_24h)} stations")
