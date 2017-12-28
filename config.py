

class Configuration(object):
    SECRET_KEY = '81824be9f077eac410a9c3e0f28bc4e2'
    DEBUG = True
    SESSION_COOKIE_HTTPONLY = False


VERSION = '2.0b'


# -------------DB------------- #
USERS = 'db/users.json'
# ---------------------------- #

# ----------WSSERVER---------- #
PORT = 8000
IP = 'localhost'
# ---------------------------- #

# ---------------------------- #
HTTP_PORT = 80
HTTP_IP = '0.0.0.0'
# ---------------------------- #
