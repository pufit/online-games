from BNB.game import Game as Bnb
import BNB.actions

from Extinguisher.game import Game as Ext
import Extinguisher.actions

from Arrows.game import Game as Arr
import Arrows.actions

from Management.game import Game as Man
import Management.actions


game_types = {
    'BNB': (Bnb, BNB.actions),
    'Ext': (Ext, Extinguisher.actions),
    'Arr': (Arr, Arrows.actions),
    'Man': (Man, Management.actions)
    }
