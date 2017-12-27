

class Button
  constructor: (@canvas, @x, @y, @width, @height, @onClick, @sprite) ->
    @selected = false


class Table
  constructor: (@canvas) ->
    @canvas.addEventListener 'mousemove', (e) =>
      @mouse_x = e.layerX
      @mouse_y = e.layerY

    @buttons = []

window.canvas = canvas = document.getElementById('canvas')
window.table = new Table(canvas)

cards = new Image()
cards.src = 'static/img/games/BNB/cards.jpg'