import json
import logging

logger = logging.getLogger('WSServer')


class Channel:
    def __init__(self, name):
        self.name = name
        self.handlers = []

    def join(self, handler):
        if handler.channel:
            handler.channel.leave(handler)
        self.handlers.append(handler)
        handler.channel = self
        self.send({
            'type': 'user_connected',
            'data': handler.get_information()
        })

    def send(self, data):
        logger.info('%s Ответ %s  %s' % (self.name, data['type'], data['data']))
        for handler in self.handlers:
            try:
                handler.ws_send(json.dumps(data))
            except:
                pass

    def leave(self, handler):
        if handler.typing:
            self.send({'type': 'user_stop_typing', 'data': {'user': handler.user, 'user_id': handler.user_id}})
        if handler in self.handlers:
            self.handlers.remove(handler)
            self.send({
                'type': 'user_disconnected',
                'data': handler.get_information()
            })
        handler.channel = None
