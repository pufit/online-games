from score_giver import give_score


def check_turn(func):
    def wrapper(self, data):
        if (self.game is not None) and (self.game.turn == self.me.id) and self.game.started:
            return func(self, data)
        else:
            return {'type': 'denied', 'data': 'Your turn have ended'}
    return wrapper


def get_information(self, _):
    resp = {'type': 'game_information', 'data': {'players': {}}}
    for player_id in self.game.players:
        player = self.game.players[player_id]
        if player.name == self.user:
            resp['data']['players'][player.name] = player.get_me_information()
        else:
            resp['data']['players'][player.name] = player.get_information()
    resp['data']['turn'] = self.game.turn
    return resp


@check_turn
def start_new_round(self, data):
    self.game.start_new_round(data)
    resp = {
        'type': 'combination_updated',
        'data': {
            'player_id': self.me.id,
            'name': self.user,
            'current_combination': self.game.current_combination.dict(),
            'turn': self.game.turn,
        }
    }
    self.game.channel.send(resp)


@check_turn
def believe(self, data):
    self.game.believe(data)
    resp = {
        'type': 'combination_updated',
        'data': {
            'player_id': self.me.id,
            'name': self.user,
            'current_combination': self.game.current_combination.dict(),
            'turn': self.game.turn,
        }
    }
    self.game.channel.send(resp)


@check_turn
def not_believe(self, data):

    # TODO: Win debug

    result, win = self.game.not_believe(data)
    result['turn'] = self.game.turn
    resp = {
        'type': 'round_ended',
        'data': result
    }
    self.game.channel.send(resp)
    if win:
        resp = {
            'type': 'game_ended',
            'data': {
                'score': self.game.score_table,
                'win': win
            }
        }
        user = self.temp.users[win]
        give_score(user, self.game.type)
        self.game.channel.send(resp)

