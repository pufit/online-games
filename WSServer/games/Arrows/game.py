from .config import *
from random import randint


class Player:
    def __init__(self, x, y, player_id, user):
        self.x, self.y = x, y
        self.id = player_id
        self.user = user

        self.direction = 0
        self.speed_x, self.speed_y = 0, 0

        self.life = Life(PLAYERS_LIFE, player_id, user)


class Life:
    def __init__(self, life, player_id, user):
        self.max_life = PLAYERS_LIFE
        self.life = life
        self.player_id = player_id
        self.user = user

    def damage(self):
        self.life -= 1


class Game:
    def __init__(self, name, channel, creator, slots, settings):

        self.MAX_PLAYERS = MAX_PLAYERS
        self.type = 'Arr'

        self.name = name
        self.slots = slots
        self.creator = creator
        self.channel = channel

        self.players = {}
        self.bullets = {}

        self.field_width = settings['width']
        self.field_height = settings['height']

        if (self.field_height > MAX_FIELD_SIZE) or (self.field_height > MAX_FIELD_SIZE):
            raise Exception('Field too large')

        self.started = False
        self.last_player_id = -1

    def add_new_player(self, user):
        if len(self.players) >= self.slots:
            raise Exception('Players limit')
        self.last_player_id += 1
        player = Player(0, 0, self.last_player_id, user)
        self.players[self.last_player_id] = player
        return player

    def start_game(self):
        pass
