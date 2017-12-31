

class WSClient
  constructor: ->
    @ws = new WebSocket('ws://localhost:8000')

    @ws.onmessage = (event) =>
      message = JSON.parse(event.data)
      @[message.type](message.data)

    @channel = {
      'name': null,
      'user_count': 0,
      'unauthorized_count': 0,
      'users': {}
    }

  send: (type, data) ->
    @ws.send(JSON.stringify({'type': type, 'data': data}))

  send_message: (message) ->
    @send('send_message', {'text': message})

  welcome: ->
    @send('get_channel_information', null)
    session = $.cookie('session')
    @send('session_auth', {'session': session}) if session

  channel_information: (data) ->
    @channel = data

  auth_ok: (data) ->
    for par of data
      @[par] = data[par]

  success_join: (data) ->
    @game = {
      'me': {}
      'players': {},
      'game': {}
    }
    @game.me.id = data.id
    @game.players = data.players
    @game.game = data.game

  new_player_connected: (data) ->
    @game.players[data.name] = data

  user_disconnected: (data) ->
    if data.user
      delete @channel.users[data.user]
      @channel.user_count -= 1
    else
      @channel.unauthorized_count -= 1

  user_connected: (data) ->
    if data.user
      @channel.users[data.user] = data
      @channel.user_count += 1
    else
      @channel.unauthorized_count += 1


window.WSClient = WSClient
