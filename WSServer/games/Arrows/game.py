from .config import *
from random import randint
import time
import _thread


# TODO: Full debug


class Player:
    def __init__(self, x, y, player_id, user, field):
        self.x, self.y = x, y
        self.id = player_id
        self.user = user

        self.field = field

        self.name = user.user

        self.direction = 0
        self.speed_x, self.speed_y = 0, 0

        self.life = PLAYERS_LIFE
        self.shooting = False

        self.score = 0

    def damage(self):
        self.life -= 1

    def action(self, act):
        if act == 'left':
            self.speed_x = -1
            self.direction = 2
        elif act == 'right':
            self.speed_x = 1
            self.direction = 0
        elif act == 'up':
            self.speed_y = -1
            self.direction = 1
        elif act == 'down':
            self.speed_y = 1
            self.direction = -1
        elif act == 'shoot':
            self.shooting = True

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x >= self.field.width:
            self.x = 0
        if self.x < 0:
            self.x = self.field.width - 1
        if self.y >= self.field.height:
            self.y = 0
        if self.y < 0:
            self.y = self.field.height - 1


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

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x >= self.field.width:
            self.x = 0
        if self.x < 0:
            self.x = self.field.width - 1
        if self.y >= self.field.height:
            self.y = 0
        if self.y < 0:
            self.y = self.field.height - 1


class Field:
    def __init__(self, width, height, max_score):
        self.width = width
        self.height = height

        self.max_score = max_score

        self.players = {}
        self.bullets = []

        self.alive_players_count = 0
        self.win = None

    def add_player(self, player):
        self.players[player.id] = player
        self.alive_players_count += 1

    def player_shoot(self, player):
        self.bullets.append(Bullet(player.x, player.y, player.direction, self))

    def update(self):
        """
        Обновляет состояние поля и всех объектов
        :return: None
        """
        for player in self.players.values():
            if not player.life:
                continue
            if player.shooting:
                self.player_shoot(player)
                player.shooting = False
            player.update()
            player.speed_x = 0
            player.speed_y = 0
        for bullet in self.bullets:
            bullet.update()
            for player in self.players.values():
                if not player.life:
                    continue
                if (player.x == bullet.x) and (player.y == bullet.y):
                    player.damage()
                    if not player.life:
                        self.alive_players_count -= 1
                        if self.alive_players_count == 1:
                            player.score += 1
                            if player.score == self.max_score:
                                self.win = player
                            self.restart()
                            break

    def restart(self):
        """
        Перезапускает игру
        :return: None
        """

        # TODO: Ошибка после первой смерти

        self.bullets = []
        self.alive_players_count = len(self.players)

        for player in self.players.values():
            player.x = randint(0, self.width - 1)
            player.y = randint(0, self.height - 1)
            player.direction = randint(-1, 2)
            player.shooting = False


class Game:
    def __init__(self, channel, creator, config):
        """
        :param channel: class Channel
        :param config: dict

        Additional settings:
            width: int
            height: int
            max_score: int
        """
        self.config = config
        self.MAX_PLAYERS = MAX_PLAYERS
        self.type = 'Arr'

        self.name = config['name']
        self.slots = config['slots']
        self.creator = creator
        self.channel = channel

        self.stop = False

        self.field = Field(config['width'], config['height'], config['max_score'])

        self.players = self.field.players

        if (self.field.width > MAX_FIELD_SIZE) or (self.field.height > MAX_FIELD_SIZE):
            raise Exception('Field too large')

        if (self.field.max_score > MAX_SCORE) or (self.field.max_score < MIN_SCORE):
            raise Exception('Max score too large or too small')

        self.started = False

    def add_new_player(self, user):
        if len(self.field.players) >= self.slots:
            raise Exception('Players limit')
        if not len(self.field.players):
            player_id = 0
        else:
            player_id = max([player.id for player in self.field.players.values()]) + 1
        player = Player(0, 0, player_id, user, self.field)
        self.field.add_player(player)
        return player

    def start_game(self):
        """
        Начинаем игру
        :return: None
        """
        self.started = True
        self.field.restart()
        while (not self.field.win) and (not self.stop):
            self.tick()
            time.sleep(TICK)

        self.channel.send({
            'type': 'game_ended',
            'data': {
                'win': self.field.win.name,
                'score': {player.name: player.score for player in self.field.players.values()}
            }
        })

        user = self.field.win.user
        user.user_stat[self.type][0] += 1
        user.temp.db_save_all()

        _thread.exit()

    def tick(self):
        """
        Один тик
        :return: None
        """
        self.field.update()
        self.channel.send({
            'type': 'tick_passed',
            'data': {
                'players': [
                    {
                        'name': player.name,
                        'life': player.life,
                        'id': player.id,
                        'x': player.x,
                        'y': player.y,
                        'direction': player.direction,
                        'score': player.score
                    } for player in self.field.players.values()
                ],
                'bullets': [
                    {
                        'x': bullet.x,
                        'y': bullet.y,
                        'direction': bullet.direction
                    } for bullet in self.field.bullets
                ],
            }
        }, log=False)

    def leave(self, player_id):
        player = self.field.players.pop(player_id)
        self.channel.send({'type': 'player_left', 'data': player.name})
