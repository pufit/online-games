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


class Bullet:
    def __init__(self, x, y, direction, field):
        self.field = field

        self.x, self.y = x, y
        self.direction = direction
        self.speed_x, self.speed_y = 0, 0
        if self.direction == 2:
            self.speed_x = -1
        elif self.direction == 1:
            self.speed_y = -1
        elif self.direction == 0:
            self.speed_x = 1
        elif self.direction == -1:
            self.speed_y = 1


class Life:
    def __init__(self, life, player_id, user):
        self.max_life = PLAYERS_LIFE
        self.life = life
        self.player_id = player_id
        self.user = user

    def damage(self):
        self.life -= 1


class Field:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.players = {}
        self.bullets = []

    def add_player(self, player):
        self.players[player.id] = player

    def player_shoot(self, player):
        self.bullets.append(Bullet(player.x, player.y, player.direction, self))


class Game:
    def __init__(self, name, channel, creator, slots, settings):

        self.MAX_PLAYERS = MAX_PLAYERS
        self.type = 'Arr'

        self.name = name
        self.slots = slots
        self.creator = creator
        self.channel = channel

        self.field = Field(settings['width'], settings['height'])

        if (self.field > MAX_FIELD_SIZE) or (self.field > MAX_FIELD_SIZE):
            raise Exception('Field too large')

        self.started = False
        self.last_player_id = -1

    def add_new_player(self, user):
        if len(self.field.players) >= self.slots:
            raise Exception('Players limit')
        self.last_player_id += 1
        player = Player(0, 0, self.last_player_id, user)
        self.field.add_player(player)
        return player

    def start_game(self):
        pass
