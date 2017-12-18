
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

  playerShoot: (player) ->
    @bullets.push(new Bullet(player.x, player.y, player.direction, @))

  addPlayer: (x, y, user) ->
    ids = player.id for player in @players
    id = if ids then Math.max.apply(0, a) else 0
    @players.push(new Player(x, y, id, @, user))

  removePlayer: (id) ->
    @bullets.splice(id, 1)

  drawDots: ->
    for i in [0...fieldWidth]
      for j in [0...fieldHeight]

        x = winFieldWidth//@width//2 + i*winFieldWidth//@width
        y = winFieldHeight//@height//2 + j*winFieldHeight//@height

        @ctx.beginPath()
        @ctx.arc(x, y, 1, 0, 2*Math.PI)
        @ctx.fillStyle = "rgb(#{@dotsColor})"
        @ctx.fill()

  update: ->
    for player in @players when player
      @playerShoot(player) if player.shooting
      player.update()
      player.speed_x = 0
      player.speed_y = 0
      player.shooting = false
    for bullet in @bullets when bullet
      bullet.update()
      for player in @players when player
        player.life.damage() if (player.x == bullet.x) and (player.y == bullet.y)

  draw: ->
    @ctx.clearRect(0, 0, @canvasWidth, @canvasHeight)
    @ctx.globalAlpha = 1
    @drawDots()
    for player in @players
      player.draw()
      player.life.draw()
    bullet.draw() for bullet in @bullets

  tick: ->
    do @update
    do @draw
    setTimeout(@tick.bind(@), 1000/fps)

  start: ->
    do @tick


class Player
  constructor: (@x, @y, @id, @field, @user) ->
    @life = new Life(10, @id, @field, @user)

    @direction = 0
    @speed_x = @speed_y = 0

    @width = winFieldWidth // fieldWidth - 2
    @height = winFieldHeight // fieldHeight - 2


    [@real_x, @real_y] = cordToCord(@x, @y, 2)

  update: ->
    @x += @speed_x
    @y += @speed_y

    @x = 0 if @x >= @field.width
    @x = @field.width - 1 if @x < 0
    @y = 0 if @y >= @field.height
    @y = @field.height - 1 if @y < 0

    [@real_x, @real_y] = cordToCord(@x, @y, 2)

  draw: ->
    @field.ctx.rotate(@direction * 90 * Math.PI/180)
    @field.ctx.drawImage(playerImages[@id], @real_x, @real_y, @width, @height)
    @field.ctx.restore()


class Bullet
  constructor: (@x, @y, @direction, @field) ->
    [@real_x, @real_y] = cordToCord(@x, @y, 3)

    @width = winFieldWidth // fieldWidth - 8
    @height = winFieldHeight // fieldHeight - 8

    @speed_x = @speed_y = 0

    @speed_x = -1 if @direction == 2
    @speed_x = 1 if @direction == 0
    @speed_y = -1 if @direction == 1
    @speed_y = 1 if @direction == -1

  update: ->
    @x += @speed_x
    @y += @speed_y

    @x = 0 if @x >= @field.width
    @x = @field.width - 1 if @x < 0
    @y = 0 if @y >= @field.height
    @y = @field.height - 1 if @y < 0

    [@real_x, @real_y] = cordToCord(@x, @y, 2)

  draw: ->
    @field.ctx.rotate(@direction * 90 * Math.PI/180)
    @field.ctx.drawImage(bulletImage, @real_x, @real_y, @width, @height)
    @field.ctx.restore()


class Life
  constructor: (@life, @id, @field, @user) ->

  draw: ->

  damage: ->


fps = 10
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
window.Bullet = Bullet
field.addPlayer(10, 10, '')
do field.start