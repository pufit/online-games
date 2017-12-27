from score_giver import give_score


def check_turn(func):
    def wrapper(self, data):
        if (self.game is not None) and (self.me.turn is not False) and (not self.me.isDead):
            return func(self, data)
        else:
            return {'type': 'failed', 'data': 'Your turn ended'}
    return wrapper


@check_turn
def end_turn(self, _):
    end_round = self.game.playerEndTurn()
    if end_round:
        __end_round(self)


def get_information(self, _):
    players = self.game.getPlayersInfo()
    resp = {
        'type': 'information',
        'data': players
    }
    return resp


def __end_round(self):

    # TODO: win debug

    end = self.game.checkForGameEnd()
    if end:
        data = {'type': 'game_over', 'data': {player.name: player.n for player in self.game.players.values()}}
        win = max(data['data'], key=lambda x: data['data'][x])
        user = self.temp.users[win]
        give_score(user, self.game.type)
        self.game.channel.send(data)
    data = {'type': 'new_round_started', 'data': ''}
    self.game.channel.send(data)


@check_turn
def sell_products(self, data):
    self.game.newRequestMaterial(self.me.id, data['count'], data['price'])
    return {'type': 'OK', 'data': ''}


@check_turn
def produce_products(self, data):
    self.game.newRequestProduce(self.me.id, data['count'])
    return {'type': 'OK', 'data': ''}


@check_turn
def buy_materials(self, data):
    self.game.newRequestMaterial(self.me.id, data['count'], data['price'])
    return {'type': 'OK', 'data': ''}


@check_turn
def sell_products(self, data):
    self.game.newRequestProduct(self.me.id, data['count'], data['price'])
    return {'type': 'OK', 'data': ''}


@check_turn
def buy_factory(self, _):
    self.game.newRequestFactory(self.me.id, 1)
    return {'type': 'OK', 'data': ''}
