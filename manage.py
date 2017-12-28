from flask import *
from config import *
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


app.config.from_object(Configuration)


if __name__ == '__main__':
    from WSServer import server

    try:
        server.run(app.secret_key)
    except OSError:
        pass

    if app.debug:
        app.run(HTTP_IP, port=HTTP_PORT)
    else:
        start_new_thread(app.run, (IP, PORT))

    while True:
        try:
            out = eval(input())
            if out is not None:
                print(out)
        except:
            traceback.print_exc()
