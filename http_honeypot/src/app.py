from flask import Flask, send_from_directory, flash, request, render_template_string, render_template,session, redirect, url_for
import os
import secrets
from time import time
from datetime import datetime
import sys
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.utils import secure_filename
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../config')))

from config import HTTP_LOG_FILE, HTTP_UPLOAD_DIR, HTTP_TEMPLATE_FOLDER
from shared.email_alert import send_email_alert
from http_config import (
    PORT, HOSTS, MAX_ATTEMPTS, TIME_WINDOW,
    fake_files, ALLOWED_EXTENSIONS, HONEY_CREDENTIALS,
    fake_shell_responses, fake_contents, posts, legit_routes
)

#import cac thu |^|

#set up linh tinh |v|

login_attempts = defaultdict(list)

#khoi tao cac thu 
app = Flask(__name__, template_folder=HTTP_TEMPLATE_FOLDER)
app.secret_key = secrets.token_hex(16)
os.makedirs(HTTP_UPLOAD_DIR, exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Ben tren la setting setup cac thu blah blah
# Ben duoi moi la real code
# He thong ghi log sieu tan tien
def log_attack(endpoint, message):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    attacker_forward_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    attacker_ip = request.remote_addr
    method = request.method
    user_agent = request.headers.get('User-Agent', 'Unknown')
    log_entry = f"[{now}] IP: {attacker_ip} | Forwarded-For: {attacker_forward_ip} | UA: {user_agent} | Method: {method} | Endpoint: {endpoint} | {message}\n"

    with open(HTTP_LOG_FILE, 'a') as f:
        f.write(log_entry)

    if any(keyword in message.lower() for keyword in ['upload', 'shell', 'password', 'sql', 'command']):
        send_email_alert(f"[ALERT] HTTP Honeypot - {endpoint}",log_entry)

#Lop nguoi dung de dang nhap
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in HONEY_CREDENTIALS:
        return User(user_id)
    return None

#kiem tra file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

#kiem tra sql inject
def are_you_bad_sql_question_mark(input_str):
    bad_sql_iden = ["'", "--", ";", " or ", " and ", "1=1", "drop", "select", "union", "="]
    for keyword in bad_sql_iden:
        if keyword.lower() in input_str.lower():
            return True
    return False
#kiem tra endpoint hop le
@app.before_request
def legit_check():
    if request.endpoint not in legit_routes:
        log_attack("/"+(request.url).split('/')[-1],"Look like a SCOUT to me")
        return "404 Not Found"

# Cac route cua web
# dang nhap
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        ip = request.remote_addr
        now = time()
        username = request.form['username']
        password = request.form['password']

        login_attempts[ip] = [t for t in login_attempts[ip] if now - t < TIME_WINDOW]
        login_attempts[ip].append(now)
        print(len(login_attempts[ip]))
        if len(login_attempts[ip])> MAX_ATTEMPTS and len(HONEY_CREDENTIALS)<8:
            if username not in HONEY_CREDENTIALS:
                HONEY_CREDENTIALS[username] = password
                user = User(username)
                login_user(user)
                log_attack('/login', f'This guy is STUBBORN aeh? Let him in with this credentials: {username}:{password}')
                send_email_alert("[ALERT] Honeypot Brute-force", f"New fake account added: {username}:{password} from {ip}")
                return redirect(url_for('dashboard'))
        if are_you_bad_sql_question_mark(username):
            log_attack('/login', f'Oh no! Enemy trying to inject us with sql VENOM: {username}')
        if are_you_bad_sql_question_mark(password):
            log_attack('/login', f'Oh no! Enemy trying to inject us with sql VENOM: {password}')
        if username in HONEY_CREDENTIALS and HONEY_CREDENTIALS[username]==password:
            user = User(username)
            login_user(user)
            log_attack('/login', f'Enemy say NAKA H ZONE with the credentials {username}:{password}!')
            return redirect(url_for('dashboard'))
        log_attack('/login',f'Enemy say DAME H ZONE with the credentials {username}:{password}!')
        return 'Wrong credentials!'
    log_attack('/login',' Enemy OHAYO the H ZONE!')
    return render_template('login.html')

# urgh..... chi la dang xuat thoi ma
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Trang chu cho nguoi dang nhap thanh cong
@app.route('/dashboard')
@login_required
def dashboard():
    log_attack('/dashboard','Enemy OHAYO to H ZONE')
    return render_template('dashboard.html',username = current_user.id)

# Well chi la trang chu thoi
@app.route('/')
def home():
    log_attack('/','Enemy OHAYO to P ZONE')
    return render_template('index.html',posts = posts)

#tim kiem mot chut nhi
@app.route('/search')
def search():
    log_attack('/search','Enemy OHAYO to searchbar-chan')
    query = request.args.get('q','')
    if are_you_bad_sql_question_mark(query):
        log_attack('/search', 'Enemy try to inject VENOM to our Honey')
    results = [post for post in posts if query.lower() in post['title'].lower()]
    return render_template('search.html', query = query, results = results)

#xem bai viet nay noi gi nao
@app.route('/post/<int:post_id>')
def post(post_id):
    log_attack(f'/post/{post_id}',f'Enemy OHAYO to post{post_id}-chan')
    post = next((p for p in posts if p['id']==post_id), None)
    if not post:
        return "Why do you search for something doesn't exist?",404
    return render_template('post.html',post = post)

#den luc dang mot cai gi do roi
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_post():
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content','')
        file = request.files.get('attachment')
        if are_you_bad_sql_question_mark(title) or are_you_bad_sql_question_mark(content):
            log_attack('/upload', f'This guy using {current_user.id} to upload post with VENOM content: {title} : {content}')
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{int(time())}_{file.filename}")
            filepath = os.path.join(HTTP_UPLOAD_DIR, filename)
            file.save(filepath)
            log_attack('/upload',f'Enemy say OHAYO and drop a package in the H ZONE, the package name: {filename}')
        elif file:
            log_attack('/upload',f'Enemy try to poison our honey, with this SPIKE: {file.filename}')
            return "We not support this kind of file yet"
        new_id = max([p['id'] for p in posts]) + 1 if posts else 1
        posts.append({'id': new_id, 'title':title, 'content':content, 'filename':filename, 'author':current_user.id})
        log_attack('/upload', f'Enemy using {current_user.id} to OHAYO and uploaded a new post: {title}')
        return redirect(url_for('post', post_id = new_id))
    return render_template('upload.html')

#toi se chua file upload o day
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(HTTP_UPLOAD_DIR, filename)
#DANGER!!!!!!!!
@app.route('/soul/power/space/time/mind/reality/smack')
def smack():
    if current_user.id == 'thanos':
        log_attack('/soul/power/space/time/mind/reality/smack', 'So this is THEEND, im happy working with you sir')
        send_email_alert(f"[ALERT] HTTP Honeypot - {endpoint}",log_entry)
        posts.clear()
        HONEY_CREDENTIALS.clear()
    else:
        log_attack('/soul/power/space/time/mind/reality/smack', 'EMERGENCY Enemy try to enter THEEND')
        return "GO BACK WHEN YOU STRONGER!"

#nhieu nguoi dung qua nhi, toi nghi chung ta can mot nguoi chi huy
@app.route('/admin')
@login_required
def admin_page():
    if current_user.id == 'admin':
        log_attack('/admin', 'Enemy OHAYO in the H ZONE')
        return render_template('admin.html')
    return "You not commander, who are you?"

#mot chut trang chi cho can phong cua chi huy
@app.route('/admin/users')
@login_required
def user_manage():
    if current_user.id == 'admin':
        log_attack('/admin/users','Enemy OHAYO in the UM ZONE')
        return render_template('users.html')
    return "You not commander, who are you?"
@app.route('/admin/files')
@login_required
def file_browser():
    if current_user.id == 'admin':
        log_attack('/admin/files','Enemy OHAYO in the F ZONE')
        return render_template('files.html', files = fake_files)
    return "You not commander, who are you?"
@app.route('/admin/files/<filename>')
@login_required
def download_fake_file(filename):
    if current_user.id == 'admin':
        log_attack(f'/admin/files/{filename}',f'Enemy OHAYO the treasure {filename} from Alantis')
        content = fake_contents.get(filename)
        if content:
            return render_template(content)
        return f"<b>File content of {filename}</b>: Access denied."
    return "You not commander, who are you?"
@app.route('/admin/terminal',methods = ['GET','POST'])
@login_required
def web_terminal():
    if current_user.id == "admin":
        output = ""
        if request.method == "POST":
            cmd = request.form.get('command')
            log_attack('/admin/terminal', f"Now they try to stir up the RABBIT Hole with {cmd}")
            if cmd in fake_shell_responses:
                output = fake_shell_responses[cmd]
            else:
                output = f"bash: {cmd}: command not found"
        return render_template('terminal.html', output = output)
    return "You not commander, who are you?"
def run():
    app.run(host=HOSTS, port=PORT)

if __name__ == '__main__':
    run()
