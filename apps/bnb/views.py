from flask import *

bnb = Blueprint('bnb', __name__, template_folder='templates', static_folder='static')


@bnb.route('/')
def game():
    return render_template('game.html')
