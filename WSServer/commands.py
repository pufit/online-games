

"""Commands"""


import json
import time

import sessions
import games
from config import *
from channel import Channel
from score_giver import give_score as __score
from _thread import start_new_thread as __start_new_thread


def perms_check(user_rights):
    def decorator(func):
        def wrapper(self, data):
            if self.user_rights >= user_rights:
                return func(self, data)
            else:
                return {'type': 'denied', 'data': 'Not enough rights'}
        return wrapper
    return decorator


def __auth(self, user, session=None, auth_type='auth_ok'):
    """
    :param self: class Handler

    :type user: str
    :param user: user name

    :type session: str, None
    :param session: flask session

    :type auth_type: str
    :param auth_type: type of answer

    :return: {
        'type': auth_type,
        'data': self.get_information(), 'session': str
    }
    """
    self.user = user
    self.user_id = self.temp.users[user]['user_id']
    self.user_rights = self.temp.users[user]['user_rights']
    self.user_stat = self.temp.users[user]['user_stat']
    for handler in self.temp.handlers:
        hand_user = handler.user
        if (hand_user == self.user) and (handler is not self):
            resp = {'type': 'disconnected', 'data': 'Disconnected!'}
            handler.ws_send(json.dumps(resp))
            handler.onClose()
    resp = {
        'type': auth_type,
        'data': self.get_information()
    }
    if not session:
        session = sessions.encode_flask_cookie(self.secret_key, resp['data'])
    resp['data']['session'] = session
    self.channel.send({
        'type': 'user_logged_in',
        'data': self.get_information()
    })
    return resp


@perms_check(0)
def auth(self, data):
    """
    :param self: class Handler
    :param data: {
        'user': str
        'password': str
    }

    :raise: You are already logged in
            Wrong login or password

    :return: __auth(self, data['user'])
    """
    if self.user:
        raise Exception('You are already logged in')
    if (data['user'] in self.temp.users) and (self.temp.users[data['user']]['password'] == data['password']):
        return __auth(self, data['user'])
    raise Exception('Wrong login or password')


@perms_check(0)
def session_auth(self, data):
    """
    :param self: class Handler
    :param data: {
        'session': str (flask session)
    }

    :return: __auth(self, user, data['session'])
    """
    session = sessions.decode_flask_cookie(self.secret_key, data['session'])
    user = session['user']
    return __auth(self, user, data['session'])


@perms_check(0)
def reg(self, data):
    """
    :param self: class Handler
    :param data: {
        'user': str,
        'password: str
    }

    :raise: This login is already in use

    :return: __auth(self, data['user'], auth_type='reg_ok')
    """
    if data["user"] not in self.temp.users:
        user_id = [self.temp.users[i]['user_id'] for i in self.temp.users]
        self.user_id = max(user_id) + 1
        self.temp.users[data["user"]] = {
            'user': data["user"],
            'password': data["password"],
            'user_rights': 1,
            'user_id': self.user_id,
            'user_stat': {i: [0, 0] for i in games.game_types}
        }
        self.temp.db_save(USERS, self.temp.users)
        return __auth(self, data['user'], auth_type='reg_ok')
    raise Exception('This login is already in use')


@perms_check(0)
def games_list(self, data):
    """
    :param self: class Handler
    :param data: None

    :return: list
    """
    lst = [{
        'name': self.temp.games[i].name,
        'creator': self.temp.games[i].creator,
        'players': len(self.temp.games[i].players),
        'type': self.temp.games[i].type,
        'slots': self.temp.games[i].slots,
        'config': self.temp.games[i].config
    } for i in self.temp.games]
    return {'type': 'ret_game_list', 'data': lst}


@perms_check(1)
def create_game(self, data):
    """
    :param self: class Handler
    :param data: {
        'name': str,
        'type': str, (see games.__init__.py)
        'slots': int,
        ... additional settings of the game
    }

    :raise: This game already exist
            Bad slots
            Bad name
            game.__init__ exceptions

    :return: dict
    """
    game = games.game_types[data['type']][0](Channel(data['name']), self.user, data)
    if self.temp.games.get(data['name']) is not None:
        raise Exception('This game already exist')
    if (data['slots'] > game.MAX_PLAYERS) or (data['slots'] < 2):
        raise Exception('Bad slots')
    if data['name'] == '':
        raise Exception('Bad name')
    leave(self, data)
    self.temp.games[data['name']] = game
    resp = {
        'type': 'game_created',
        'data': {
            'name': data['name'],
            'players': 0,
            'type': data['type'],
            'slots': data['slots']
        }
    }
    self.temp.main_channel.send(resp)
    return {'type': 'create_game_ok', 'data': None}


@perms_check(1)
def join(self, data):
    """
    :param self: class Handler

    :type data: str
    :param data: name of the game

    :raise: This game dose not exist
            Game already started

    :return: dict
    """
    if not self.temp.games.get(data):
        raise Exception('This game dose not exist')
    if self.temp.games[data].started:
        raise Exception('Game already started')
    if self.game:
        leave(self, None)
    self.game = self.temp.games[data]
    self.me = self.game.add_new_player(self)
    resp = {
        'type': 'new_player_connected',
        'data': {
            'id': self.me.id,
            'name': self.user,
            'player_information': self.get_information()
        }
    }
    self.game.channel.send(resp)
    self.temp.main_channel.send({
        'type': 'game_player_connected',
        'data': data
    })
    self.game.channel.join(self)
    resp = {
        'type': 'success_join',
        'data': {
            'id': self.me.id,
            'players': {
                self.game.players[player].name:
                    {
                    'id': player,
                    'name': self.game.players[player].name,
                    'player_information': self.game.players[player].user.get_information()
                } for player in self.game.players
            }
        }
    }
    return resp


@perms_check(1)
def start_game(self, data):
    if not self.game:
        raise Exception('You are not connected to any game')
    if self.user != self.game.creator:
        raise Exception('You are not creator of this game')
    __start_new_thread(self.game.start_game, tuple())
    self.game.channel.send({'type': 'game_started', 'data': ''})
    return {'type': 'game', 'data': ''}


@perms_check(0)
def leave(self, data):
    if not self.game:
        return None
    if self.game.started:
        __score(self, self.game.type, -1)
    else:
        self.temp.main_channel.send({
            'type': 'game_player_left',
            'data': self.game.name
        })
    self.game.leave(self.me.id)
    if len(self.game.players) == 0:
        self.temp.games.pop(self.game.name)
        self.game.stop = True
        if not self.game.started:
            self.temp.main_channel.send({
                'type': 'game_deleted',
                'data': self.game.name
            })
    self.game = None
    self.me = None
    self.temp.main_channel.join(self)
    return {'type': 'leave_ok', 'data': 'Left'}


@perms_check(1)
def action(self, data):
    action_type = data['action_type'].replace('__', '')
    resp = games.game_types[self.game.type][1].__getattribute__(action_type)(self, data)
    return {'type': 'action_%s_ok' % action_type, 'data': resp}


@perms_check(1)
def start_typing(self, data):
    if self.typing:
        raise Exception('You are already typing')
    self.typing = True
    self.channel.send({'type': 'user_start_typing', 'data': {'user': self.user, 'user_id': self.user_id}})
    return {'type': 'start_typing_ok', 'data': ''}


@perms_check(1)
def stop_typing(self, data):
    if not self.typing:
        raise Exception('You are not typing')
    self.typing = False
    self.channel.send({'type': 'user_stop_typing', 'data': {'user': self.user, 'user_id': self.user_id}})
    return {'type': 'stop_typing_ok', 'data': ''}


@perms_check(0)
def send_message(self, data):
    """
    :param self: class Handler
    :param data: {
        'text': str
    }
    :return: dict
    """
    resp = {
        'type': 'message',
        'data': {
            'name': self.user,
            'rights': self.user_rights,
            'time': time.time(),
            'text': data['text']
        }
    }
    self.channel.send(resp)
    return {'type': 'send_ok', 'data': ''}


@perms_check(0)
def get_channel_information(self, data):
    if self.channel:
        users = {}
        user_count = 0
        for handler in self.channel.handlers:
            user_count += 1
            if handler.user:
                users[handler.user] = handler.get_information()
        return {
            'type': 'channel',
            'data': {
                'name': self.channel.name,
                'users_count': user_count,
                'unauthorized_count': user_count - len(self.channel.handlers),
                'users': users
            }
        }
    return {'type': 'channel_information', 'data': ''}


@perms_check(0)
def ping(self, data):
    """
    :param self: None
    :param data: send time or None
    :return: dict
    """
    if not data:
        return {'type': 'pong', 'data': 'Pong!'}
    return {'type': 'pong', 'data': time.time() - data}


def error(self, data):
    """
    System method
    :param self: None
    :param data: None
    :return: dict
    """
    return {'type': 'error', 'data': 'Bad request'}

