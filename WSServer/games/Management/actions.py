

def end_turn(self, data):
    self.turn = False
    end_round = self.game.playerEndTurn()
    if end_round:
        __end_round(self)


def __end_round(self):
    end = self.game.checkForGameEnd()
    if end:
        data = {'type': 'game_over', 'data': end}
        self.game.channel.send(data)
    data = {'type': 'new_round_started', 'data': ''}
    self.game.channel.send(data)
    for handler in self.game.handlers:
        handler.turn = True


def sell_products(self, data):
    self.game.newRequestMaterial(self.me.id, data['count'], data['price'])


def produce_products(self, data):
    self.game.newRequestProduce(self.me.id, data['count'])


def buy_materials(self, data):
    self.game.newRequestMaterial(self.me.id, data['count'], data['price'])


def buy_factory(self, data):
    self.game.newRequestFactory(self.me.id, 1)