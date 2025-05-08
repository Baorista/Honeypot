import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../')))

from config import HTTP_REPORT_FILE
def extract_stat_from_logs(logs):
	stats = {
		"forward_from": set(),
		"ips": set(),
		"user_agents": set(),
		"endpoints": set()
	}
	for log in logs:
		if 'forwarded_for' in log:
			stats['forward_from'].add(log['forwarded_for'])
		if 'ip' in log:
			stats['ips'].add(log['ip'])
		if 'ua' in log:
			stats['user_agents'].add(log['ua'])
		if 'endpoint' in log:
			stats['endpoints'].add(log['endpoint'])
	return stats
def save_report_to_json(stats,attacks,path = HTTP_REPORT_FILE):
	output = {
		'stat':{
			'forward_from': list(stats['forward_from']),
			'unique_ips': list(stats['ips']),
			'user_agents': list(stats['user_agents']),
			'endpoints': list(stats['endpoints']),
		},
		'attacks': {k: [log for log in v] for k, v in attacks.items()}
	}
	with open(path,'w') as f:
		json.dump(output,f,indent=4, default=str)