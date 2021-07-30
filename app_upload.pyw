from werkzeug.utils import secure_filename
import os
import socket

from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)



class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = []
users.append(User(id=1, username='zbs', password='password'))
users.append(User(id=2, username='admin', password='secret'))
users.append(User(id=3, username='new', password='sss111'))


app = Flask(__name__)
app.secret_key = 'nobodynkonwsexceptme'


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']
        found = False
        for my_user in users:
            if my_user.username == username:
                found = True
        if not found:
            return redirect(url_for('login'))
        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('upload'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect(url_for('login'))


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)+'\\user_files'  # get current path
        upload_path = os.path.join(basepath, '', secure_filename(
            f.filename))  # the folder must be created before hand
        f.save(upload_path)
    return render_template('upload.html')


# if __name__ == '__main__':
ip_address = socket.gethostbyname(socket.gethostname())
print('Your ip address is: ', ip_address)
app.run(host='0.0.0.0', port=80)
