from collections import defaultdict

def classify_attacks(logs):
	attacks = defaultdict(list)

	for log in logs:
		message = log['message'].lower()
		if 'stubborn' in message:
			attacks['brute_force'].append(log)
		elif 'venom' in message:
			attacks['sql_injection'].append(log)
		elif 'rabbit' in message:
			attacks['execute_command'].append(log)
		elif 'naka' in message:
			attacks['credentials_found'].append(log)
		elif 'dame' in message:
			attacks['login_attempt'].append(log)
		elif 'ohayo' in message:
			attacks['web_navigate'].append(log)
		elif 'spike' in message:
			attacks['malicious_file_upload'].append(log)
		elif 'theend' in message:
			attacks['the_end'].append(log)
		elif 'scout' in message:
			attacks['api_scanning'].append(log)
		else:
			attacks['other'].append(log)
	return attacks