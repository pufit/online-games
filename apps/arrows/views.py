from flask import *

arrows = Blueprint('arrows', __name__, template_folder='templates', static_folder='static')


@arrows.route('/')
def game():
    return render_template('game.html')
