
# TODO: Life draw


class Field
  constructor: (@canvas, @game) ->
    @width = @game.config.width
    @height = @game.config.height

    @jqcanvas = $('#canvas')
    @canvasHeight = @canvasWidth = @canvas.height = @canvas.width = Math.min(@jqcanvas.width() - winAdditionalWidth , @jqcanvas.height())
    @canvas.width += winAdditionalWidth
    @jqcanvas.width(@canvas.width)
    @jqcanvas.height(@canvas.height)
    @ctx = @canvas.getContext('2d')

    @dotsColor = "173, 192, 219"

    @players = []
    @bullets = []

  drawDots: ->
    for i in [0...@width]
      for j in [0...@height]

        x = @canvasWidth//@width//2 + i*@canvasWidth//@width
        y = @canvasHeight//@height//2 + j*@canvasHeight//@height

        @ctx.beginPath()
        @ctx.arc(x, y, 1, 0, 2*Math.PI)
        @ctx.fillStyle = "rgb(#{@dotsColor})"
        @ctx.fill()

  addNewPlayer: (id, user) ->
    player = new Player(0, 0, id, @, user)
    @players.push(player)
    return player

  update: (players, bullets) ->
    for player in players when player.life
      up_player = @players[player.id]
      for par of player
        up_player[par] = player[par]
    @bullets = []
    for bullet in bullets
      @bullets.push(new Bullet(bullet.x, bullet.y, bullet.direction, @))
    @draw()

  draw: ->
    @ctx.clearRect(0, 0, @canvasWidth, @canvasHeight)
    @ctx.globalAlpha = 1
    @drawDots()
    player.draw() for player in @players
    bullet.draw() for bullet in @bullets

  cordToCord: (x, y, k) ->
    return [x*@canvasHeight // @width + k, y * @canvasHeight // @height + k]


class Player
  constructor: (@x, @y, @id, @field, @user) ->
    @life = 10

    @direction = 0

    @width = @field.canvasWidth // @field.width - 2
    @height = @field.canvasHeight // @field.height - 2


    [@real_x, @real_y] = @field.cordToCord(@x, @y, 2)

  draw: ->
    [@real_x, @real_y] = @field.cordToCord(@x, @y, 2)
    @field.ctx.save()
    @field.ctx.translate(@real_x + @width / 2, @real_y + @height / 2)
    @field.ctx.rotate(@direction * 90 * Math.PI/180)
    @field.ctx.drawImage(playerImages[@id], -@width / 2, -@height / 2, @width, @height)
    @field.ctx.restore()


class Bullet
  constructor: (@x, @y, @direction, @field) ->
    [@real_x, @real_y] = @field.cordToCord(@x, @y, 3)

    @width = @field.canvasWidth // @field.width - 8
    @height = @field.canvasHeight // @field.height - 8

  draw: ->
    [@real_x, @real_y] = @field.cordToCord(@x, @y, 2)
    @field.ctx.save()
    @field.ctx.translate(@real_x + @width / 2, @real_y + @height / 2)
    @field.ctx.rotate(@direction * 90 * Math.PI/180)
    @field.ctx.drawImage(bulletImage, -@width / 2, -@height / 2, @width, @height)
    @field.ctx.restore()


class ArrWS extends WSClient
  auth_ok: (data) ->
    super data
    @send('join', gameName)

  do_action: (data) ->
    @send('action', {'action_type': 'do_action', 'direction': data})

  success_join: (data) ->
    super data
    window.field = field = new Field(document.getElementById('canvas'), data.game)
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


winAdditionalWidth = 200

bulletImage = new Image()
bulletImage.src = 'static/img/bullet.png'

window.playerImages = playerImages = [new Image(), new Image()]
playerImages[0].src = 'static/img/player1.png'
playerImages[1].src = 'static/img/player2.png'

window.ArrWS = ArrWS = new ArrWS()
