A simple Honeypot for learning purposes
To run it, run the honeypot.py
A menu is gonna drop down from it
Enter 1 to run SSH, 2 for FTP, 3 for HTTP, 4 to run all, or 0 to stop

HTTP:

This is a blog website built with Flask. All the settings are in the Honeypot/http_honeypot/config/http_config.py. This web can detect BruteForce, Web Scanning, SQL Injection, and Malicious file uploads. All the logs will go to Honeypot/http_honeypot/logs/access.log. Then you can analyze it with analysis.py in the analysis folder. Right now, I just classify attacks, statistics parameters like the number of IPs, endpoints, user agents, etc. When you run analysis.py, the result gonna go to report.json. And then, if you want, you can visualize it with visualize.py in src. I don't have much knowledge about the real Honeypot, so if there's anything wrong, please point it out.
