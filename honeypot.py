import subprocess
import os
import sys


def menu():
    print("=== Honeypot Menu ===")
    print("1. Chạy SSH honeypot")
    print("2. Chạy FTP honeypot")
    print("3. Chạy HTTP honeypot")
    print("4. Chạy tất cả")
    print("0. Thoát")

def run_ssh():
    ssh_path = os.path.join(os.path.dirname(__file__),"ssh_honeypot", "src", "ssh_honeypot.py")
    return subprocess.Popen([sys.executable, ssh_path])

def run_ftp():
    ftp_path = os.path.join(os.path.dirname(__file__),"ftp_honeypot", "src", "ftp_honeypot.py")
    return subprocess.Popen([sys.executable, ftp_path])

def run_http():
    http_path = os.path.join(os.path.dirname(__file__),"http_honeypot", "src", "app.py")
    return subprocess.Popen([sys.executable, http_path])    
def main():
    menu()
    choice = input("What do u want to run babe? <3: ").strip()
    processes = []
    if choice == "1":
        run_ssh()
    elif choice =="2":
        run_ftp()
    elif choice =="3":
        run_http()
    elif choice =="4":
        processes.append(run_ssh())
        processes.append(run_ftp())
        processes.append(run_http())
    elif choice =="0":
        sys.exit(0)
    else:
        print("HUH!?")
        sys.exit(1)
    try:
        for p in processes:
            if p:
                p.wait()
    except KeyboardInterrupt:
        print("Shutting down")
        for p in processes:
            if p:
                p.terminate()
if __name__ == "__main__":
    main()