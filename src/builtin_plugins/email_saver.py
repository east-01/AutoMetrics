import shutil
import smtplib
from email.message import EmailMessage
import os
from pathlib import Path
import time

from src.data.data_repository import DataRepository
from src.data.filters import *
from src.parameter_utils import ConfigurationException
from src.plugin_mgmt.plugins import Saver
from src.program_data import ProgramData
from src.utils.config_checker import verify_sections_exist
from src.utils.timeutils import from_unix_ts, seconds_to_compact

class EmailSaver(Saver):
    """ Will zip the output directory and attach it to an email to be sent to the destination
            addresss as specified in the config. """
    
    def verify_config_section(self, config_section):
        pass
    
    def save(self, prog_data: ProgramData, config_section: dict, base_path: str):

        FOLDER_TO_ZIP = "my_folder"
        ZIP_NAME = "results.zip"

        EMAIL = "you@gmail.com"
        APP_PASSWORD = "APP_PASSWORD"
        SMTP_SERVER = "127.0.0.1"
        SMTP_PORT = 1025

        root_path = Path(base_path).resolve()
        zip_file_path = root_path.parent / ZIP_NAME
        print(f"  Zipping output directory: {root_path}")
        # Zip
        shutil.make_archive(str(zip_file_path).replace(".zip", ""), "zip", root_dir=str(root_path))

        # Email
        start_time_formatted = from_unix_ts(prog_data.program_start_ts)
        runtime_formatted = seconds_to_compact(time.time() - prog_data.program_start_ts)

        msg = EmailMessage()
        msg["From"] = EMAIL
        msg["To"] = EMAIL
        msg["Subject"] = f"AutoMetrics results from {start_time_formatted}"
        msg.set_content(f"Results generated from configuration {prog_data.args.config} on {start_time_formatted}, taking {runtime_formatted}.")

        with open(zip_file_path, "rb") as f:
                msg.add_attachment(
                        f.read(),
                        maintype="application",
                        subtype="zip",
                        filename=zip_file_path.name
                )

        is_auth = False
        print(f"  Sending email to \"{EMAIL}\" with {"SSL" if is_auth else "no SSL"}.")
        if(is_auth):
              with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.login(EMAIL, APP_PASSWORD)
                server.send_message(msg)
        else:
              with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.set_debuglevel(1)
                server.send_message(msg)

        print(f"  Sent.")
