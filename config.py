# honeypot/config.py
import os

# Lấy thư mục gốc của project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Các đường dẫn thành phần cua http
HTTP_DIR = os.path.join(BASE_DIR, 'http_honeypot')
HTTP_LOG_DIR = os.path.join(HTTP_DIR, 'logs')
HTTP_LOG_FILE = os.path.join(HTTP_LOG_DIR, 'access.log')
HTTP_UPLOAD_DIR = os.path.join(HTTP_DIR, 'uploads')
HTTP_TEMPLATE_FOLDER = os.path.join(HTTP_DIR, 'templates')
HTTP_REPORT_FILE = os.path.join(HTTP_LOG_DIR, 'report.json')


#SSH
SSH_PORT = 2223
SSH_HOSTS = '0.0.0.0'
SSH_DIR = os.path.join(BASE_DIR, 'ssh_honeypot')
SSH_KEY = os.path.join(SSH_DIR,'key','server.key')
SSH_LOG_DIR = os.path.join(SSH_DIR, 'log')
SSH_AUTH_LOG =  os.path.join(SSH_LOG_DIR,'auth.log')
SSH_ALERT_LOG =  os.path.join(SSH_LOG_DIR, 'alerts.log')
SSH_CMD_LOG = os.path.join(SSH_LOG_DIR, 'cmd_logs.json')
SSH_CMD_CSV = os.path.join(SSH_LOG_DIR, 'cmd_logs.csv')
SSH_CREDENTIALS = os.path.join(SSH_DIR, 'credentials', 'creds.txt')

#FTP 
FTP_DIR = os.path.join(BASE_DIR, 'ftp_honeypot','src')
FTP_LOG_DIR = os.path.join(FTP_DIR, 'logs')
FTP_LOG_FILE = os.path.join(FTP_LOG_DIR, 'honeypot_log.json')
FTP_LOG_ANA = os.path.join(FTP_LOG_DIR, 'analysis_report.json')