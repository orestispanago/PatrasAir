import json
import os

from dotenv import load_dotenv

dname = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(dname, "config.json")
load_dotenv(os.path.join(dname, ".env"))

with open(config_file, "r", encoding="utf8") as f:
    configs = json.load(f)

READ_KEY = os.getenv("READ_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
FTP_IP = os.getenv("FTP_IP")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_DIR = configs.get("FTP_DIR")
