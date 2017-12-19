

def do_action(self, data):
    possible_actions = ['left', 'right', 'up', 'down', 'shoot']
    if data in possible_actions:
        self.me.action(data)
