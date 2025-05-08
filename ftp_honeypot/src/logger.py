import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')))

from config import FTP_LOG_FILE

def write_log(data, filename=FTP_LOG_FILE):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(filename, "a") as logfile:
            json.dump(data, logfile)
            logfile.write("\n")
        print("Log entry added successfully.")
    except Exception as e:
        print(f"Error writing to log file: {e}")
