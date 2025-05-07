import locale
import logging

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from sensors import SENSOR_NAMES_GR
from utils import mkdir_if_not_exists

logger = logging.getLogger(__name__)

LARGE_FONT = 28
MEDIUM_FONT = 14

LIGHT_BLUE = "#43dbff"
GREEN = "#96cd4f"
YELLOW = "#ffff00"
RED = "#fc3903"
DARK_RED = "#990100"


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


def add_logos(ax, sensor_name="sensor_a", img_path="lapup_aether_logos.png"):
    pic = plt.imread(img_path)
    ax.imshow(pic)
    ax.text(
        500,
        -200,
        sensor_name,
        fontsize=MEDIUM_FONT,
        weight="bold",
        ha="center",
        va="center",
    )
    ax.axis("off")


def pm_to_aqi_color(pm_value):
    # if type(pm_value) is str:
    #     return LIGHT_BLUE
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


def add_last_value(last_dt, last_value, ax):
    if not last_value:
        show_no_data(ax)
    else:
        last_pm_value = int(last_value)
        last_dt_fmt = last_dt.strftime("%d %b %H:%M")
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


def plot_timeseries(df, ax, col="pm2.5"):
    if df.count().values[0] <= 1:
        show_no_data(ax)
    else:
        ax.plot(
            df.index,
            df[col],
            ".-",
            color="black",
            linewidth=1,
            markersize=0.5,
        )
        yaxis_color_aqi(ax)
        format_date(df, ax)


def plot_sensor_timeseries(
    df_7d,
    df_24h,
    col="pm2.5",
    name="sensor_a",
    folder="plots",
    last_dt=None,
    last_value=None,
    suffix="",
):
    fig, axes = plt.subplots(
        2, 2, figsize=(10, 6), gridspec_kw={"width_ratios": [1, 2]}
    )
    ax_top_left = axes[0][0]
    ax_top_right = axes[0][1]
    ax_lower_left = axes[1][0]
    ax_lower_right = axes[1][1]

    plot_timeseries(df_24h, ax_top_right, col=col)
    plot_timeseries(df_7d, ax_lower_right, col=col)
    add_logos(ax_lower_left, sensor_name=SENSOR_NAMES_GR.get(name))
    add_last_value(last_dt, last_value, ax_top_left)
    fig.subplots_adjust(hspace=0.3)
    mkdir_if_not_exists(folder)
    figname = f"{folder}/{name}{suffix}.jpg"
    plt.savefig(figname)
    plt.close()
    logger.debug(f"Plotted {figname} ")


def plot_sensors_timeseries(sensors, folder="plots", col="pm2.5", suffix=""):
    locale.setlocale(locale.LC_ALL, "el_GR.utf8")
    logger.debug(f"Set locale: {locale.getlocale(locale.LC_ALL)}")
    for sensor in sensors:
        plot_sensor_timeseries(
            sensor.data_7d,
            sensor.data_24h,
            col=col,
            name=sensor.name,
            folder=folder,
            last_dt=sensor.last_dt,
            last_value=sensor.last_value,
            suffix=suffix,
        )
    logger.info(f"Plotted {len(sensors)} sensors timeseries")
