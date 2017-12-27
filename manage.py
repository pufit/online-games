from flask import *
from _thread import start_new_thread
import sys
import os
import traceback
from apps.main_pages.views import main_pages
from apps.arrows.views import arrows
from apps.bnb.views import bnb
from apps.extinguisher.views import extinguisher
from apps.management.views import management

sys.path.append(os.getcwd() + '\\WSServer\\games')
sys.path.append(os.getcwd() + '\\WSServer')


app = Flask(__name__, static_folder=None, template_folder=None)
app.register_blueprint(main_pages)
app.register_blueprint(arrows, url_prefix='/arrows')
app.register_blueprint(bnb, url_prefitx='/bnb')
app.register_blueprint(extinguisher, url_prefix='/ext')
app.register_blueprint(management, url_prefix='/management')

app.config.update(
    SECRET_KEY='81824be9f077eac410a9c3e0f28bc4e2',
    DEBUG=True,
    SESSION_COOKIE_HTTPONLY=False
)

VERSION = '2.0b'


if __name__ == '__main__':
    from WSServer import server

    server.VERSION = VERSION

    try:
        server.run(app.secret_key)
    except OSError:
        pass

    if app.debug:
        app.run('0.0.0.0', port=80)
    else:
        start_new_thread(app.run, ('0.0.0.0', 80))

    while True:
        try:
            out = eval(input())
            if out is not None:
                print(out)
        except:
            traceback.print_exc()
