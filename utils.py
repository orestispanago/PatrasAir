import json
import logging
import os

logger = logging.getLogger(__name__)


with open("station_names_gr.json", "r", encoding="utf8") as f:
    STATION_NAMES_GR = json.load(f)


def mkdir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.debug(f"Created local directory {dir_path}")