from flask import *
from _thread import start_new_thread
import sys
import os
import traceback


sys.path.append(os.getcwd() + '\\WSServer\\games')
sys.path.append(os.getcwd() + '\\WSServer')


app = Flask(__name__)

app.config.update(
    SECRET_KEY='81824be9f077eac410a9c3e0f28bc4e2',
    DEBUG=True,
    SESSION_COOKIE_HTTPONLY=False
)

VERSION = '2.0b'


@app.route('/')
def lobby():
    return render_template('pages/lobby.html', table=render_template('games/BNB/game.html'))


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if session.get('user'):
        return redirect('')
    if request.method == 'GET':
        return render_template('pages/auth.html')
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')
        if (user in server.db.users) and (server.db.users[user]['password'] == password):
            user = server.db.users[user]
            session['user'] = user['user']
            session['user_id'] = user['user_id']
            session['user_rights'] = user['user_rights']
            return redirect('')
        return render_template('pages/auth.html', error='Неверный логин или пароль!')
    abort(418)


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if session.get('user'):
        return redirect('')
    if request.method == 'GET':
        return render_template('pages/reg.html')
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        if (user not in server.db.users) and (password == repassword):
            user_id = max([server.db.users[i]['user_id'] for i in server.db.users]) + 1
            session['user'] = user
            session['user_id'] = user_id
            session['user_rights'] = 1
            server.db.users[session['user']] = {
                'user': session['user'],
                'password': session['password'],
                'user_rights': 1,
                'user_id': user_id,
                'user_stat': {}
            }
            server.db.db_save(server.USERS, server.db.users)
            return redirect('')
        return render_template('pages/auth.html', error='Такой пользователь уже существует, или пароли не совпадают!')
    abort(418)


@app.route('/debug')
def debug():
    raise Exception('Debug')


@app.route('/user/<user_id>')
def user_data(user_id):
    for user in server.db.users:
        if server.db.users[user]['user_id'] == user_id:
            user_rights = server.db.users[user]['user_rights']
            me = False
            if session.get('user') == user:
                me = True
            return render_template('pages/pa.html',
                                   user=user,
                                   user_id=user_id,
                                   user_rights=user_rights,
                                   me=me)


@app.route('/user/<user_id>/edit')
def user_data_edit(user_id):
    pass


@app.route('/arrows')
def arrows():
    return render_template('games/Arr/game.html')


@app.route('/chat')
def chat():
    return render_template('pages/chat.html')


if __name__ == '__main__':
    from WSServer import server

    server.VERSION = VERSION

    try:
        server.run(app.secret_key)
    except OSError:
        pass

    if app.debug:
        app.run('0.0.0.0', port=80)
    else:
        start_new_thread(app.run, ('0.0.0.0', 80))

    while True:
        try:
            out = eval(input())
            if out is not None:
                print(out)
        except:
            traceback.print_exc()
