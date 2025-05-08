import re
from collections import Counter, defaultdict
import pprint
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../')))

from config import HTTP_LOG_FILE
LOG_PATTERN = re.compile(
	r"\[(?P<timestamp>.*?)\] IP: (?P<ip>.*?) \| Forwarded-For: (?P<forwarded_for>.*?) \| UA: (?P<ua>.*?) \| Method: (?P<method>.*?) \| Endpoint: (?P<endpoint>.*?) \| (?P<message>.*)"
)

def parse_log_file(log_path):
	logs = []
	with open(log_path, 'r') as f:
		for line in f:
			match = LOG_PATTERN.match(line.strip())
			if match:
				log_data = match.groupdict()
				logs.append(log_data)
	return logs
logs = parse_log_file(HTTP_LOG_FILE)
# with open('/opt/honeypot/http_honeypot/analysis/test.txt', 'w') as f:
#     for log in logs:
#         f.write(str(log))
