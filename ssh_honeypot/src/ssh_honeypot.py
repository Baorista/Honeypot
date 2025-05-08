import csv
import logging
import threading
from logging.handlers import RotatingFileHandler
import socket
import paramiko
from datetime import datetime
import json
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')))

from config import SSH_KEY, SSH_AUTH_LOG, SSH_ALERT_LOG, SSH_CMD_LOG, SSH_CMD_CSV, SSH_CREDENTIALS, SSH_HOSTS, SSH_PORT

# Constants
logging_format = logging.Formatter('%(message)s')
SSH_BANNER = "SSH-2.0-MySSHServer_1.1"
host_key = paramiko.RSAKey(filename=SSH_KEY)

# Loggers
auth_logger = logging.getLogger("Auth Logger")
auth_logger.setLevel(logging.INFO)
auth_handler = RotatingFileHandler(SSH_AUTH_LOG, maxBytes=5 * 1024, backupCount=3)
auth_handler.setFormatter(logging_format)
auth_logger.addHandler(auth_handler)

alert_logger = logging.getLogger("Alerts Logger")
alert_logger.setLevel(logging.INFO)
alert_handler = RotatingFileHandler(SSH_ALERT_LOG, maxBytes=5 * 1024, backupCount=3)
alert_handler.setFormatter(logging_format)
alert_logger.addHandler(alert_handler)

def generate_realistic_banner():
    now = datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y")
    lines = [
        "Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-101-generic x86_64)\n\r",
        " * Documentation:  https://help.ubuntu.com\n\r",
        " * Management:     https://landscape.canonical.com\n\r",
        " * Support:        https://ubuntu.com/advantage\n\r",
        "\n\r",
        f"System information as of {now}\n\r",
        "",
        f"{'System load:':<20}0.42      {'Users logged in:':<20}1\n\r",
        f"{'Memory usage:':<20}35%      {'IPv4 address for eth0:':<20}127.0.1.1\n\r",
        f"{'Swap usage:':<20}5%        {'Processes:':<20}107\n\r",
        "",
        f"Last login: {now} from 127.0.1.1\n\r",
    ]
    return '\n'.join(lines)

DANGEROUS_COMMANDS = ['rm', 'wget', 'curl', 'nc', 'nmap', 'scp', 'ssh']

def is_dangerous(cmd):
    return any(cmd.startswith(d) for d in DANGEROUS_COMMANDS)

def log_command(ip, username, command):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log in key=value format for easier parsing
    log_line = f"timestamp={timestamp} ip={ip} username={username} command=\"{command}\""
    auth_logger.info(log_line)

    # Save as CSV
    with open(SSH_CMD_CSV, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, ip, username, command])

    # Save as JSON
    log_entry = {"timestamp": timestamp, "ip": ip, "username": username, "command": command}
    with open(SSH_CMD_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    # Log dangerous commands separately
    if is_dangerous(command):
        alert_logger.warning(f"timestamp={timestamp} ip={ip} DANGEROUS_COMMAND=\"{command}\"")

def get_current_dir(fs, cwd):
    current = fs['/']
    for d in cwd[1:]:
        current = current.get(d, {})
    return current

def emulated_shell(channel, client_ip, username):
    def send(text):
        channel.send(text.encode())

    def sendln(text):
        channel.send(text.encode() + b'\r\n')

    fake_fs = {
        '/': {
            'custardA.config': 'CONFIG: allow_remote_root=1',
            'flag.txt': 'CTF{you_found_me}',
            'notes.txt': 'todo: upload backdoor\ncheck crontab',
            'fake_dir': {
                'secret.txt': 'Top secret inside dir1',
                'file1.txt': '123',
                'file2.txt': '456',
            }
        }
    }

    cwd = ['/']
    prompt = 'custardA$ '
    command = ''
    history = []
    history_index = -1
    cursor_pos = 0

    send(prompt)

    while True:
        char = channel.recv(1)
        if not char:
            break

        if char == b'\x1b':
            seq = channel.recv(2)
            if seq == b'[A':
                if history:
                    history_index = max(0, history_index - 1)
                    command = history[history_index].decode()
                    cursor_pos = len(command)
                    send('\r\x1b[K' + prompt + command)
            elif seq == b'[B':
                if history:
                    history_index = min(len(history) - 1, history_index + 1)
                    command = history[history_index].decode()
                    cursor_pos = len(command)
                    send('\r\x1b[K' + prompt + command)
            elif seq == b'[C':
                if cursor_pos < len(command):
                    send('\x1b[C')
                    cursor_pos += 1
            elif seq == b'[D':
                if cursor_pos > 0:
                    send('\x1b[D')
                    cursor_pos -= 1
            continue

        if char in (b'\x7f', b'\x08'):
            if cursor_pos > 0:
                command = command[:cursor_pos - 1] + command[cursor_pos:]
                cursor_pos -= 1
                send('\r\x1b[K' + prompt + command)
                send('\r' + prompt + command[:cursor_pos])
            continue

        if char == b'\r':
            send('\r\n')
            cmd = command.strip()
            if cmd:
                history.append(cmd.encode())
                history_index = len(history)

            current = get_current_dir(fake_fs, cwd)

            if cmd == 'exit':
                sendln("Goodbye!")
                channel.close()
                break

            elif cmd == 'whoami':
                sendln(f"{username}")

            elif cmd == 'clear':
                send('\033c')

            elif cmd == 'history':
                for i, h in enumerate(history[-10:], 1):
                    sendln(f'{i}  {h.decode()}')

            elif cmd == 'uname -a':
                sendln("Linux honeypot 5.15.0-101-generic #1 SMP x86_64 GNU/Linux")

            elif cmd.startswith('touch '):
                filename = cmd.split(' ', 1)[1]
                current[filename] = ''
                sendln('')

            elif cmd.startswith('echo '):
                if '>' in cmd:
                    parts = cmd.split('>', 1)
                    content = parts[0].strip()[5:].strip().strip('"')
                    filename = parts[1].strip()
                    current[filename] = content
                    sendln('')
                else:
                    sendln(cmd[5:])

            elif cmd.startswith('cd '):
                path = cmd[3:].strip()
                if path == '..':
                    if len(cwd) > 1:
                        cwd.pop()
                elif path in current and isinstance(current[path], dict):
                    cwd.append(path)
                else:
                    sendln(f"cd: no such file or directory: {path}")

            elif cmd == 'pwd':
                sendln('/' + '/'.join(cwd[1:]) if len(cwd) > 1 else '/')

            elif cmd == 'ls':
                sendln('  '.join(current.keys()))

            elif cmd.startswith('mkdir '):
                dirname = cmd.split(' ', 1)[1]
                if dirname in current:
                    sendln(f"mkdir: cannot create directory '{dirname}': File exists")
                else:
                    current[dirname] = {}
                    sendln('')

            elif cmd.startswith('rmdir '):
                dirname = cmd.split(' ', 1)[1]
                if dirname in current and isinstance(current[dirname], dict):
                    if current[dirname]:
                        sendln(f"rmdir: failed to remove '{dirname}': Directory not empty")
                    else:
                        del current[dirname]
                        sendln('')
                else:
                    sendln(f"rmdir: failed to remove '{dirname}': No such directory")

            elif cmd.startswith('cat '):
                filename = cmd.split(' ', 1)[1]
                if filename in current:
                    sendln(current[filename])
                else:
                    sendln(f"cat: {filename}: No such file or directory")

            else:
                sendln(f"bash: {cmd}: command not found")

            log_command(client_ip, username=username, command=cmd)
            command = ''
            cursor_pos = 0
            send(prompt)
            continue

        try:
            char_decoded = char.decode()
        except:
            continue

        command = command[:cursor_pos] + char_decoded + command[cursor_pos:]
        cursor_pos += 1
        send('\r\x1b[K' + prompt + command)
        send('\r' + prompt + command[:cursor_pos])

class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, input_username=None, input_passwd=None, creds_dict=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_passwd = input_passwd
        self.creds_dict = creds_dict
        self.authenticated_username = None

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return 'password'

    def check_auth_password(self, username, password):
        auth_logger.info(f'Client {self.client_ip} attempted connection with username: {username}, password: {password}')
        alert_logger.info(f'{self.client_ip}, {username}, {password}')

        if self.input_username and self.input_passwd:
            if username == self.input_username and password == self.input_passwd:
                self.authenticated_username = username
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        elif self.creds_dict and username in self.creds_dict:
            if self.creds_dict[username] == password:
                self.authenticated_username = username
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

def client_handle(client, addr, username=None, password=None, creds_dict=None):
    client_ip = addr[0]
    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        server = Server(client_ip=client_ip, input_username=username, input_passwd=password, creds_dict=creds_dict)

        transport.add_server_key(host_key)
        transport.start_server(server=server)

        channel = transport.accept(100)
        if channel is None:
            return

        username_used = server.authenticated_username or "unknown"
        banner = generate_realistic_banner()
        channel.send(banner.encode())
        emulated_shell(channel, client_ip, username=username_used)

    except Exception as error:
        print(error)
    finally:
        try:
            transport.close()
        except:
            pass
        client.close()

def honey_pot(address, port, username=None, password=None, creds_dict=None):
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))

    socks.listen(100)
    print(f"SSH server is listening on port {port}.")

    while True:
        try:
            client, addr = socks.accept()
            threading.Thread(target=client_handle, args=(client, addr, username, password, creds_dict)).start()
        except Exception as error:
            print("!!! Exception - Could not open new client connection !!!")
            print(error)
def running():
    print("Run mode:")
    print("1. Username:password")
    print("2. Credentials dict")
    choice = input("Your choice?: ")
    username = None
    password = None
    creds_dict = {}
    if choice == '1':
        username = input("Enter fake username: ")
        password = input("Enter fake password: ")
        print(f"Run with {username}:{password}")
    elif choice == '2':
        print("Run with Credentials dict")
        print("Check the dict at /honeypot/ssh_honeypot/credentials/creds.txt")
        with open(SSH_CREDENTIALS, 'r') as f:
            for line in f:
                if ':' in line:
                    user, pw = line.strip().split(':', 1)
                    creds_dict[user] = pw
    else:
        print("Run in default mode with Credentials dict")
        with open(SSH_CREDENTIALS, 'r') as f:
            for line in f:
                if ':' in line:
                    user, pw = line.strip().split(':', 1)
                    creds_dict[user] = pw
    honey_pot(SSH_HOSTS, SSH_PORT, username, password, creds_dict)
running()
    
