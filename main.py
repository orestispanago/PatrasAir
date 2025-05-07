import glob
import logging
import logging.config
import os
import traceback

from downloader import download_sensors_data
from plot_map import plot_scatter_map
from plot_timeseries import plot_sensors_timeseries
from sensors import read_sensors
from uploader import ftp_upload_files

dname = os.path.dirname(__file__)
os.chdir(dname)

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main():
    logger.info(f"{'-' * 15} START {'-' * 15}")

    """ ============================== PATRAS ============================== """
    logger.debug("Starting Patras task...")
    download_sensors_data(sensors_csv="sensors_patras.csv", dir="data/patras")
    sensors_patras = read_sensors(
        sensors_csv="sensors_patras.csv", data_dir="data/patras"
    )
    plot_sensors_timeseries(sensors_patras, folder="plots/patras")
    plot_scatter_map(sensors_patras, fname="plots/patras/map.jpg")
    local_files_patras = glob.glob("plots/patras/*.jpg")
    ftp_upload_files(local_files_patras)
    logger.debug("Patras task complete.")

    """ ============================== TITAN ============================== """
    logger.debug("Starting Titan task...")
    download_sensors_data(
        sensors_csv="sensors_titan.csv", dir="data/titan", download_daily=True
    )
    sensors_titan = read_sensors(
        sensors_csv="sensors_titan.csv", data_dir="data/titan"
    )
    plot_sensors_timeseries(sensors_titan, folder="plots/titan", suffix="_pm25")
    plot_sensors_timeseries(
        sensors_titan, folder="plots/titan", col="pm10.0", suffix="_pm10"
    )
    local_files_titan = glob.glob("plots/titan/*.jpg")
    daily_csv_files_titan = glob.glob("data/titan/*/daily*.csv")
    ftp_upload_files(local_files_titan)
    ftp_upload_files(daily_csv_files_titan)
    logger.debug("Titan task complete.")

    logger.info(f"{'-' * 15} SUCCESS {'-' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
