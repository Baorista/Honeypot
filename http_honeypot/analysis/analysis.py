import classify_attack
import stat_ioc
import parse_logs
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../')))

from config import HTTP_LOG_FILE
logs = parse_logs.parse_log_file(HTTP_LOG_FILE)
classi = classify_attack.classify_attacks(logs)
statc = stat_ioc.extract_stat_from_logs(logs)
stat_ioc.save_report_to_json(statc,classi)