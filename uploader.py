import logging
import os
from ftplib import FTP

from config import FTP_DIR, FTP_IP, FTP_PASSWORD, FTP_USER

logger = logging.getLogger(__name__)


def ftp_upload_file(ftp_session, local_path, remote_path, ftp_dir=FTP_DIR):
    with open(local_path, "rb") as f:
        ftp_session.storbinary(f"STOR {remote_path}", f)
    logger.debug(
        f"Uploaded {local_path} to {remote_path} at FTP: {ftp_dir}{remote_path}"
    )


def ftp_upload_files(local_files, ftp_dir=FTP_DIR):
    with FTP(FTP_IP, FTP_USER, FTP_PASSWORD) as ftp:
        ftp.cwd(ftp_dir)
        for local_file in local_files:
            base_name = os.path.basename(local_file)
            ftp_upload_file(ftp, local_file, base_name, ftp_dir)
    logger.info(f"Uploaded {len(local_files)} files at FTP: '{ftp_dir}'")
