from flask import *
from WSServer import server
import WSServer.games

main_pages = Blueprint('main_pages', __name__, template_folder='templates', static_folder='static')


@main_pages.route('/')
def lobby():
    return render_template('lobby.html')


@main_pages.route('/auth', methods=['POST', 'GET'])
def auth():
    if session.get('user'):
        return redirect('')
    if request.method == 'GET':
        return render_template('auth.html')
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')
        if (user in server.db.users) and (server.db.users[user]['password'] == password):
            user = server.db.users[user]
            session['user'] = user['user']
            session['user_id'] = user['user_id']
            session['user_rights'] = user['user_rights']
            return redirect('')
        return render_template('auth.html', error='Неверный логин или пароль!')
    abort(418)


@main_pages.route('/reg', methods=['POST', 'GET'])
def reg():
    if session.get('user'):
        return redirect('')
    if request.method == 'GET':
        return render_template('reg.html')
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
                'user_stat': {i: [0, 0] for i in WSServer.games.game_types}
            }
            server.db.db_save_all()
            return redirect('')
        return render_template('reg.html', error='Такой пользователь уже существует, или пароли не совпадают!')
    abort(418)


@main_pages.route('/user/<user_id>')
def user_data(user_id):
    user_information = server.db.get_user_id_information(int(user_id))
    return render_template('pa.html', user_information=user_information)


@main_pages.route('/chat/<channel_id>')
def chat(channel_id):
    return render_template('chat.html', channel_id=channel_id)


@main_pages.route('/debug')
def debug():
    raise Exception('Debug')
