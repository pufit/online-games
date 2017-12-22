
cordToCord = (x, y, k) ->
  return [x*winFieldWidth // fieldWidth + k, y * winFieldHeight // fieldHeight + k]

window.cordToCord = cordToCord

class Field
  constructor: (@canvas, @width, @height) ->
    @ctx = @canvas.getContext('2d')
    @canvasWidth = @canvas.width = winFieldWidth + winAdditionalWidth
    @canvasHeight = @canvas.height = winFieldHeight

    @dotsColor = "173, 192, 219"

    @players = []
    @bullets = []

  drawDots: ->
    for i in [0...fieldWidth]
      for j in [0...fieldHeight]

        x = winFieldWidth//@width//2 + i*winFieldWidth//@width
        y = winFieldHeight//@height//2 + j*winFieldHeight//@height

        @ctx.beginPath()
        @ctx.arc(x, y, 1, 0, 2*Math.PI)
        @ctx.fillStyle = "rgb(#{@dotsColor})"
        @ctx.fill()

  addNewPlayer: (id, user) ->
    @players.push(new Player(0, 0, id, @, user))

  update: (players, bullets) ->
    for player in players when player.life
      up_player = @players[player.id]
      for par of player
        up_player[par] = player[par]
    for bullet, i in bullets
      @bullets[i].x = bullet.x
      @bullets[i].y = bullet.y
      @bullets[i].direction = bullet.direction
    @draw()

  draw: ->

    # TODO: Ошибка отрисовки

    @ctx.clearRect(0, 0, @canvasWidth, @canvasHeight)
    @ctx.globalAlpha = 1
    @drawDots()
    for player in @players
      player.draw()
      player.life.draw()
    bullet.draw() for bullet in @bullets


class Player
  constructor: (@x, @y, @id, @field, @user) ->
    @life = new Life(10, @id, @field, @user)

    @direction = 0

    @width = winFieldWidth // fieldWidth - 2
    @height = winFieldHeight // fieldHeight - 2


    [@real_x, @real_y] = cordToCord(@x, @y, 2)

  draw: ->
    [@real_x, @real_y] = cordToCord(@x, @y, 2)
    @field.ctx.rotate(@direction * 90 * Math.PI/180)
    @field.ctx.drawImage(playerImages[@id], @real_x, @real_y, @width, @height)
    @field.ctx.restore()


class Bullet
  constructor: (@x, @y, @direction, @field) ->
    [@real_x, @real_y] = cordToCord(@x, @y, 3)

    @width = winFieldWidth // fieldWidth - 8
    @height = winFieldHeight // fieldHeight - 8

  draw: ->
    [@real_x, @real_y] = cordToCord(@x, @y, 2)
    @field.ctx.rotate(@direction * 90 * Math.PI/180)
    @field.ctx.drawImage(bulletImage, @real_x, @real_y, @width, @height)
    @field.ctx.restore()


class Life
  constructor: (@life, @id, @field, @user) ->

  draw: ->


class ArrWS extends WSClient
  auth_ok: (data) ->
    super data
    @send('join', 'test')

  do_action: (data) ->
    @send('action', {'action_type': 'do_action', 'direction': data})

  success_join: (data) ->
    super data
    for player in Object.values(data.players)
      field.addNewPlayer(player.id, player.player_information)
    $(document).keydown (event) =>
      if event.which == 37
        @do_action('left')
      if event.which == 39
        @do_action('right')
      if event.which == 38
        @do_action('up')
      if event.which == 40
        @do_action('down')
      if event.which == 32
        @do_action('shoot')

  new_player_connected: (data) ->
    super data
    field.addNewPlayer(data.id, data.player_information)

  tick_passed: (data) ->
    field.update(data.players, data.bullets)





winFieldWidth = 400
winFieldHeight = 400
winAdditionalWidth = 200
fieldWidth = 20
fieldHeight = 20

bulletImage = new Image()
bulletImage.src = 'static/img/games/Arr/bullet.png'

window.playerImages = playerImages = [new Image(), new Image()]
playerImages[0].src = 'static/img/games/Arr/player1.png'
playerImages[1].src = 'static/img/games/Arr/player2.png'



field = new Field(document.getElementById('canvas'), fieldWidth, fieldHeight)
window.field = field

window.ArrWS = ArrWS = new ArrWS()