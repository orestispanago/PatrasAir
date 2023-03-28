import logging
import os
from ftplib import FTP

from config import FTP_DIR, FTP_IP, FTP_PASSWORD, FTP_USER

logger = logging.getLogger(__name__)


def ftp_upload_file(ftp_session, local_path, remote_path):
    with open(local_path, "rb") as f:
        ftp_session.storbinary(f"STOR {remote_path}", f)
    logger.debug(f"Uploaded {local_path} to {remote_path} at FTP")


def ftp_upload_files(local_files):
    with FTP(FTP_IP, FTP_USER, FTP_PASSWORD) as ftp:
        ftp.cwd(FTP_DIR)
        for local_file in local_files:
            base_name = os.path.basename(local_file)
            ftp_upload_file(ftp, local_file, base_name)
    logger.info(f"Uploaded {len(local_files)} files to FTP")
