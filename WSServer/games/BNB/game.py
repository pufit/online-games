import random
from .config import *


class Player:
    def __init__(self, user, player_id):
        self.name = user.user
        self.user = user

        self.id = player_id

        self.inventory = []
        self.n = 0

    def get_information(self):
        resp = {
            'id': self.id,
            'cards': len(self.inventory)
        }
        return resp

    def get_me_information(self):
        resp = {
            'id': self.id,
            'cards': self.sorted_cards(self.inventory)
        }
        return resp

    def sorted_cards(self, cards):
        return list(map(self.card_conversion, sorted(map(self.card_conversion, cards))))

    @staticmethod
    def card_conversion(card):
        if card == 'J':
            return 11
        elif card == 'Q':
            return 12
        elif card == 'K':
            return 13
        elif card == 'A':
            return 14
        elif card == 11:
            return 'J'
        elif card == 12:
            return 'Q'
        elif card == 13:
            return 'K'
        elif card == 14:
            return 'A'
        elif (type(card) == str) and (int(card) > 1) and (int(card) < 11):
            return int(card)
        elif (type(card) == int) and (card > 1) and (card < 11):
            return str(card)
        raise ValueError


class Game:
    def __init__(self, name, channel, creator, slots, _):

        self.MAX_PLAYERS = MAX_PLAYERS
        self.type = 'BNB'

        self.name = name
        self.slots = slots
        self.creator = creator
        self.players = {}
        self.channel = channel

        self.started = False
        self.turn = None
        self.last_player_id = - 1

        self.player_count_after_start = 0

        self.table = []
        self.publ_table = []
        self.deck = []
        self.current_cards = None
        self.last = False

        self.score_table = {}

    def add_new_player(self, user):
        if len(self.players) >= self.slots:
            raise Exception('Players limit')
        self.last_player_id += 1
        player = Player(user, self.last_player_id)
        self.players[self.last_player_id] = player
        return player

    def start_game(self):
        self.player_count_after_start = len(self.players)
        self.turn = '0'
        self.started = True
        self.deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
        random.shuffle(self.deck)
        random.shuffle(self.deck)
        random.shuffle(self.deck)

        for i in self.players:
            self._player_add_card(i, self.deck[int(i)::len(self.players)])

    def _player_add_card(self, player_id, cards):
        self.players[player_id].inventory += cards
        inventory = self.players[player_id].inventory[:]
        for card in inventory:
            if self.players[player_id].inventory.count(card) == 4:
                for _ in range(4):
                    self.players[player_id].inventory.remove(card)
                self.channel.send({'type': 'cards_out', 'data': card})

    def _player_turn(self, np=True):
        turns = list(self.players)
        turns.sort()
        if len(turns) == 0:
            return None
        index = turns.index(self.turn)
        if np:
            if index + 1 == len(turns):
                index = 0
            else:
                index += 1
        else:
            if index - 1 < 0:
                index = len(turns) - 1
            else:
                index -= 1
        self.turn = turns[index]

    def _table_add_cards(self, cards, player_id):
        temp_table = []
        if len(cards) > 5:
            raise Exception('You can not shell out more than 5 cards')
        for i in cards:
            try:
                self.players[player_id].inventory.remove(i)
                temp_table.append(i)
            except ValueError:
                for card in temp_table:
                    self.players[player_id].inventory.append(card)
                raise Exception('You do not have this cards')
        self.table.append(temp_table)
        self.publ_table.append(len(temp_table))
        if not len(self.players[player_id].inventory):
            self.last = True

    def start_new_round(self, cards, cards_value):
        if self.current_cards:
            raise Exception('Invalid action')
        self._table_add_cards(cards, self.turn)
        self.current_cards = cards_value
        self._player_turn()

    def believe(self, cards):
        if (not self.current_cards) or self.last:
            raise Exception('Invalid action')
        self._table_add_cards(cards, self.turn)
        self._player_turn()

    def not_believe(self, card_id):
        if (not self.current_cards) and (len(self.table[-1]) < card_id - 1):
            raise Exception('Bad card id')
        result = {
            'name': self.players[self.turn].name,
            'id': self.turn,
            'took_name': self.players[self.turn].name,
            'took_id': self.turn,
            'card_id': card_id,
            'card_value': self.table[-1][card_id],
            'current_cards': self.current_cards
        }
        if self.table[-1][card_id] != self.current_cards:
            self._player_turn(np=False)
            result['took_name'] = self.players[self.turn].name
            result['took_id'] = self.turn
        else:
            self.find_out_players()
        for i in self.table:
            self._player_add_card(self.turn, i)

        self.table = []
        self.publ_table = []
        self.current_cards = None
        self.last = False
        self._player_turn()
        for player in self.players.values():
            player.n += 1
        win = self.find_out_players()
        
        return result, win

    def find_out_players(self):
        players = self.players.copy()
        for player_id in players:
            player = self.players[player_id]
            if len(player.inventory) == 0:
                if len(self.players) == 2:
                    self.score_table[self.players[self.turn].name] += 1
                    return True
                self.score_table[player.name] = player.n
                self.kill_player(player_id)

    def kill_player(self, player_id):
        self.players[player_id].user.user_stat[self.type][0] += 1
        if self.turn == player_id:
            self._player_turn()
        name = self.players.pop(player_id).name

        self.channel.send({'type': 'player_out', 'data': name})

    def leave(self, player_id):
        if self.turn == player_id:
            self._player_turn()
        inv = self.players[player_id].inventory
        name = self.players.pop(player_id).name

        for i in self.players:
            self._player_add_card(i, inv[int(i)::len(self.players)])

        self.channel.send({'type': 'player_left', 'data': name})
