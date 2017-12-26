#!c:\Python34\python.exe
# -*- coding: utf-8 -*-

from config import *
from channel import Channel
import json


class Db:
    def __init__(self):
        self.users = {}
        self.db_update()

        self.games = {}

        self.handlers = []

        self.main_channel = Channel('main')
    
    def db_update(self):
        with open(USERS, 'r', encoding='utf-8') as f:
            self.users = json.load(f)

    @staticmethod
    def db_save(name, value):
        with open(name, 'w', encoding='utf-8') as f:
            json.dump(value, f, indent=2)
        return True

    def db_save_all(self):
        with open(USERS, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2)
        return True
