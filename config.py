import json

with open("config.json", "r", encoding="utf8") as f:
    configs = json.load(f)

READ_KEY = configs.get("READ_KEY")
GOOGLE_MAPS_API_KEY = configs.get("GOOGLE_MAPS_API_KEY")
FTP_IP = configs.get("FTP_IP")
FTP_USER = configs.get("FTP_USER")
FTP_PASSWORD = configs.get("FTP_PASSWORD")
FTP_DIR = configs.get("FTP_DIR")
