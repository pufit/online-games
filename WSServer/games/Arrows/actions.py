

def do_action(self, data):
    if not self.game.started:
        raise Exception('Game have did not start yet')
    possible_actions = ['left', 'right', 'up', 'down', 'shoot']
    if data['direction'] in possible_actions:
        self.me.action(data['direction'])
