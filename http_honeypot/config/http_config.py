import os
import secrets
from collections import defaultdict

PORT = 8080
HOSTS = '0.0.0.0'
MAX_ATTEMPTS = 10
TIME_WINDOW = 60
fake_files = ['config.php', 'secrets.env', 'passwords.txt', 'id_rsa']
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

HONEY_CREDENTIALS = {
    'admin':'admin123',
    'root':'toor',
    'johnsmith':'shadow',
    'ifyouknow':'youknow',
    'Shiori':'Novelite',
    'NinoIna':'Takodachi',
    'thanos':'ASD123fgh$%^'
}
fake_shell_responses = {
                "ls": "secrets.txt  config.php  passwords.txt  id_rsa  backup.zip",
                "whoami": "root",
                "pwd": "/var/www/html",
                "id": "uid=0(root) gid=0(root) groups=0(root)",
                "uname -a": "Linux honeypot 5.15.0-91-generic #101-Ubuntu SMP x86_64 GNU/Linux",
                "cat secrets.txt": "API_KEY=1234567890abcdef\nSECRET_KEY=qwertyuiop",
                "cat config.php": "<?php\n$host = 'localhost';\n$user = 'admin';\n$pass = 'admin123';\n?>",
                "cat passwords.txt": "admin:123456\nroot:toor\njohn:shadow",
                "cat id_rsa": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAvf...\n-----END RSA PRIVATE KEY-----",
                "netstat -tulnp": "tcp   0   0 0.0.0.0:22    0.0.0.0:*   LISTEN  1234/sshd\ntcp   0   0 0.0.0.0:80    0.0.0.0:*   LISTEN  5678/apache2"
            }
fake_contents = {
        "config.php": "config_php.html",
        "secrets.txt": "secrets_txt.html",
        "id_rsa": "id_rsa.html",
        "passwords.txt": "password_txt.html",
}
posts = [
    {'id': 1, 'title': 'Giới thiệu về Flask', 'content': 'Flask là một micro web framework của Python...'},
    {'id': 2, 'title': 'Lập trình với Python', 'content': 'Python rất mạnh mẽ và đơn giản...'},
]
legit_routes = ['login','logout','dashboard','home','search','post','upload_post','uploaded_file','smack','admin_page','user_manage','file_browser','download_fake_file','web_terminal']
