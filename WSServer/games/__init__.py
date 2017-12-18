from BNB.game import Game as Bnb
import BNB.actions

from Extinguisher.game import Game as Ext
import Extinguisher.actions


game_types = {
        'BNB': (Bnb, BNB.actions),
        'Ext': (Ext, Extinguisher.actions),
        'Arr': tuple()
    }
