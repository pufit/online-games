'''
Тут есть несколько покерных терминов, которые google переводчик не знает
Сам я их нашел на английской википедии
rank – значение карты без масти ("K", "10"...)
suit – масть карты
trips – очередное название тройки
quads – каре
hand – почти синоним комбинации
'''

import enum
from .config import *
from random import shuffle
from copy import deepcopy


def shuffled(arr):
    result = deepcopy(arr)
    for _ in range(3):
        shuffle(result)
    return result


class Card:
    cards_ranks = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')
    cards_suits = '0123'  # ♡♧♢♤

    def __init__(self, rank, suit):
        if rank not in Card.cards_ranks:
            raise ValueError('Invalid cards rank')
        if suit not in Card.cards_suits:
            raise ValueError('Invalid cards suit')
        self.rank = rank
        self.suit = suit

    @staticmethod
    def index(rank):
        return Card.cards_ranks.index(rank)

    def __str__(self):
        return self.rank + self.suit

    def __lt__(self, other):
        assert isinstance(other, Card)
        return Card.index(self.rank) < Card.index(other.rank)

    def __eq__(self, other):
        assert isinstance(other, Card)
        return self.rank == other.rank and self.suit == other.suit


@enum.unique
class Hands(enum.IntEnum):
    high_card, pair, two_pairs, trips, straight, flush, full_house, quads, straight_flush, flush_royal = range(10)


class Combination:
    combinations_names = ('high_card', 'pair', 'two_pairs', 'trips', 'straight',
                          'flush', 'full_house', 'quads', 'straight_flush', 'flush_royal')

    def __init__(self, combinations_data):
        self.hand = self.combinations_names.index(combinations_data['name'])
        if (self.hand == Hands.straight or self.hand == Hands.straight_flush)\
                and Card.index(combinations_data['high_rank']) < Card.index('5'):
            raise ValueError('Invalid straights high card')
        if self.hand in (Hands.high_card, Hands.pair, Hands.trips, Hands.quads):
            self.rank = combinations_data['rank']
        elif self.hand in (Hands.straight, Hands.flush, Hands.straight_flush):
            self.rank = combinations_data['high_rank']
            if self.hand != Hands.straight:
                self.suit = combinations_data['suit']
        elif self.hand == Hands.two_pairs:
            self.first_rank, self.second_rank = combinations_data['ranks']
        elif self.hand == Hands.full_house:
            self.pairs_rank = combinations_data['pairs_rank']
            self.trips_rank = combinations_data['trips_rank']
        elif self.hand == Hands.flush_royal:
            self.suit = combinations_data['suit']
        else:
            raise ValueError('Invalid hand')

    def dict(self):
        result = {'name': self.combinations_names[self.hand]}
        if self.hand in (Hands.high_card, Hands.pair, Hands.trips, Hands.quads):
            result.update(rank=self.rank)
        elif self.hand in (Hands.straight, Hands.flush, Hands.straight_flush):
            result.update(high_rank=self.rank)
            if self.hand != Hands.straight:
                result.update(suit=self.suit)
        elif self.hand == Hands.two_pairs:
            result.update(ranks=[self.first_rank, self.second_rank])
        elif self.hand == Hands.full_house:
            result.update(pairs_rank=self.pairs_rank, trips_rank=self.trips_rank)
        elif self.hand == Hands.flush_royal:
            result.update(suit=self.suit)
        else:
            raise ValueError('Invalid hand')
        return result

    def __lt__(self, other):
        assert isinstance(other, Combination)
        if self.hand != other.hand:
            return self.hand < other.hand
        if self.hand in (Hands.high_card, Hands.pair, Hands.trips, Hands.straight,
                         Hands.flush, Hands.quads, Hands.straight_flush):
            return Card.index(self.rank) < Card.index(other.rank)
        if self.hand == Hands.two_pairs:
            min1, max1 = sorted([Card.index(self.first_rank), Card.index(self.second_rank)])
            min2, max2 = sorted([Card.index(other.first_rank), Card.index(other.second_rank)])
            if max1 != max2:
                return max1 < max2
            return min1 < min2
        if self.hand == Hands.full_house:
            if self.trips_rank != other.trips_rank:
                return self.trips_rank < other.trips_rank
            return self.pairs_rank < other.pairs_rank
        if self.hand == Hands.flush_royal:
            return False
        raise ValueError('Invalid hand')

    def exist_in(self, cards):
        ranks = [card.rank for card in cards]
        suits = [card.suit for card in cards]
        if self.hand == Hands.high_card:
            return self.rank in ranks
        if self.hand == Hands.pair:
            return ranks.count(self.rank) >= 2
        if self.hand == Hands.two_pairs:
            return ranks.count(self.first_rank) >= 2 and ranks.count(self.second_rank) >= 2
        if self.hand == Hands.trips:
            return ranks.count(self.rank) >= 3
        if self.hand == Hands.straight:
            if self.rank == '5':
                return {'A', '2', '3', '4', '5'} <= set(ranks)
            for i in range(Card.index(self.rank), Card.index(self.rank) - 5, -1):
                if Card.cards_ranks[i] not in ranks:
                    return False
            return True
        if self.hand == Hands.flush:
            return suits.count(self.suit) >= 5 and Card(self.rank, self.suit) in cards
        if self.hand == Hands.full_house:
            return ranks.count(self.trips_rank) >= 3 and ranks.count(self.pairs_rank) >= 2
        if self.hand == Hands.quads:
            return ranks.count(self.rank) == 4
        if self.hand == Hands.straight_flush:
            if self.rank == '5':
                for card in (Card(rank, self.suit) for rank in ('A', '2', '3', '4', '5')):
                    if card not in cards:
                        return False
                return True
            for i in range(Card.index(self.rank), Card.index(self.rank) - 5, -1):
                if Card(Card.cards_ranks[i], self.suit) not in cards:
                    return False
            return True
        if self.hand == Hands.flush_royal:
            for card in (Card(rank, self.suit) for rank in ('10', 'J', 'Q', 'K', 'A')):
                if card not in cards:
                    return False
            return True
        raise ValueError('Invalid hand')


class Player:
    def __init__(self, user, player_id):
        self.name = user.user
        self.user = user

        self.id = player_id
        self.inventory = []
        self.cards_count = 2

        self.n = 0

    def get_information(self):
        return {
            'id': self.id,
            'cards': self.cards_count
        }

    def get_me_information(self):
        self.inventory.sort()
        return {
            'id': self.id,
            'cards': [{'rank': self.inventory[i].rank,
                       'suit': self.inventory[i].suit} for i in range(len(self.inventory))]
        }


class Game:
    def __init__(self, name, channel, creator, slots, _):

        self.MAX_PLAYERS = MAX_PLAYERS
        self.type = 'Ext'

        self.name = name
        self.creator = creator
        self.slots = slots
        self.last_player_id = -1
        self.channel = channel

        self.started = False

        self.players = {}
        self.turn = None
        self.deck = []
        self.current_combination = None

        self.score_table = {}

    def add_new_player(self, user):
        if len(self.players) >= self.slots:
            raise OverflowError('Players limit')
        self.last_player_id += 1
        player = Player(user, self.last_player_id)
        self.players[self.last_player_id] = player
        return player

    def start_game(self):
        del self.last_player_id
        if len(self.players) < 2:
            raise RuntimeError('Too few players')
        self.turn = '0'
        self.started = True
        self.deck = shuffled([Card(rank, suit) for rank in Card.cards_ranks for suit in Card.cards_suits])
        if len(self.players) == 2:
            for player_id in self.players:
                self.players[player_id].cards_count = 3
        self._give_out_cards()

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

    def _give_out_cards(self):
        for player_id in self.players:
            for _ in range(self.players[player_id].cards_count):
                self.players[player_id].inventory.append(self.deck.pop())

    def start_new_round(self, combinations_data):
        if self.current_combination or not self.started:
            raise RuntimeError('Invalid action')
        self.current_combination = Combination(combinations_data)
        self._player_turn()

    def believe(self, combinations_data):
        if not self.current_combination or not self.started:
            raise RuntimeError('Invalid action')
        comb = Combination(combinations_data)
        if not comb > self.current_combination:
            raise ValueError('Too low combination')
        self.current_combination = comb
        self._player_turn()

    def not_believe(self):
        if not self.current_combination or not self.started:
            raise RuntimeError('Invalid action')
        result = {
            'name': self.players[self.turn].name,
            'id': self.turn,
            'took_name': self.players[self.turn].name,
            'took_id': self.turn,
            'current_combination': self.current_combination.dict()
        }
        players_cards = []
        for player_id in self.players:
            players_cards += self.players[player_id].inventory
            self.players[player_id].inventory.clear()
        if self.current_combination.exist_in(players_cards):
            self.players[self.turn].cards_count += 1
        else:
            self._player_turn(np=False)
            self.players[self.turn].cards_count += 1
            result['took_name'] = self.players[self.turn].name
            result['took_id'] = self.turn
        self.deck = shuffled(self.deck + players_cards)
        self.current_combination = None
        win = self.find_out_players()
        for player in self.players.values():
            player.n += 1
        self._player_turn()
        self._give_out_cards()
        return result, win

    def find_out_players(self):
        players = self.players.copy()
        for player_id in players:
            player = self.players[player_id]
            if player.card_count == 8:
                if len(self.players) == 1:
                    return self.players[self.turn].name
                self.score_table[player.name] = player.n
                self.kill_player(player_id)

    def kill_player(self, player_id):
        if self.turn == player_id:
            self._player_turn()
        name = self.players.pop(player_id).name

        self.channel.send({'type': 'player_out', 'data': name})

    def leave(self, player_id):
        name = self.players[player_id].name
        self.kill_player(player_id)
        self.channel.send({'type': 'player_left', 'data': name})
