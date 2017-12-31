from flask import *
from WSServer import server

arrows = Blueprint('arrows', __name__, template_folder='templates', static_folder='static')


@arrows.route('/<name>')
def game(name):
    if name not in server.db.games:
        abort(404)
    return render_template('game.html', name=name, test=server.db.handlers)
