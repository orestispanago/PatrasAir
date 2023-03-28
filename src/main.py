import glob
import logging
import logging.config
import os
import traceback

from config import GOOGLE_MAPS_API_KEY
from datatasks.download import download_sensors_data
from datatasks.upload import ftp_upload_files
from models.sensors import read_sensors
from plotting.map import plot_scatter_map
from plotting.timeseries import plot_sensors_timeseries

dname = os.path.dirname(__file__)
os.chdir(dname)

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def run_task(region, map=True, timeseries=True):
    logger.info(f"{'-' * 10} Running task for region: {region} {'-' * 10}")
    data_dir = f"../data/{region}"
    sensors_csv = f"../sensors/{region}.csv"
    plots_dir = f"../plots/{region}"
    basemap = f"../basemaps/{region}.pickle"
    map_name = f"{plots_dir}/map_{region}.jpg"
    download_sensors_data(sensors_csv=sensors_csv, dir=data_dir)
    sensors = read_sensors(sensors_csv, data_dir=data_dir)
    if timeseries:
        plot_sensors_timeseries(sensors, folder=plots_dir)
    if map:
        plot_scatter_map(sensors, fname=map_name, basemap=basemap)
    local_files = glob.glob(f"{plots_dir}/*.jpg")
    # ftp_upload_files(local_files)
    logger.info(f"{'-' * 10} Finished task for region: {region} {'-' * 10}")


def main():
    logger.info(f"{'-' * 15} START {'-' * 15}")
    run_task("thrace")
    run_task("patras")
    run_task("skyros")
    run_task("nafpaktos")
    run_task("thermi")
    logger.info(f"{'-' * 15} SUCCESS {'-' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
