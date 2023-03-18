import glob
import logging
import logging.config
import os
import traceback

from downloader import download_qc_data
from uploader import ftp_upload_files
from plotter import plot_stations

dname = os.path.dirname(__file__)
os.chdir(dname)

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main():
    download_qc_data(dir="site-data")
    # local_files = glob.glob("site-data/*/*.csv")
    # ftp_upload_files(local_files)
    plot_stations(folder="plots")
    logger.info(f"{'-' * 15} SUCCESS {'-' * 15}")
    


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
