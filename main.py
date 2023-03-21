import glob
import logging
import logging.config
import os
import traceback

from downloader import download_qc_data
from map import plot_scatter_map
from plotter import plot_sensors_timeseries
from sensors import get_sensors
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
    download_qc_data(dir="data")
    sensors = get_sensors("sensors.csv")
    plot_sensors_timeseries(sensors, folder="plots")
    plot_scatter_map(sensors, fname="plots/map.png")
    local_files = glob.glob("plots/*.png")
    ftp_upload_files(local_files)
    logger.info(f"{'-' * 15} SUCCESS {'-' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
