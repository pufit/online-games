from random import choice
from .config import *


class Player():
    def __init__(self, player_id):
        self.id = player_id
        self.money = 10000
        self.materials = 4
        self.products = 2
        self.factories = 2
        self.isDead = False
        self.turn = False

    def getInfo(self):
        return {'money': self.money,
                'materials': self.materials,
                'products': self.products,
                'factories': self.factories,
                'isDead': self.isDead
                }

    def payTaxes(self):
        self.money -= self.materials * 300
        self.money -= self.products * 500
        self.money -= self.factories * 1000
        if self.money <= 0:
            self.isDead = True
            return True
        return False


class Factory:
    def __init__(self, player_id):
        self.owner = player_id
        self.age = 0

    def grow(self):
        self.age += 1
        if self.age == 4:
            return True
        return False


class Game:
    def __init__(self, name, channel, creator, slots=MAX_PLAYERS):
        
        self.MAX_PLAYERS = MAX_PLAYERS
        self.type = 'Man'

        self.name = name
        self.channel = channel
        self.creator = creator
        self.slots = slots

        self.gameLevel = 1
        self.gameLevelUpdateTable = [
            [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 5],  # [4, 4, 2, 1, 1]
            [1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 5],  # [3, 4, 3, 1, 1]
            [1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5],  # [1, 3, 4, 3, 1]
            [1, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5],  # [1, 1, 3, 4, 3]
            [1, 2, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5]  # [1, 1, 2, 4, 4]
        ]  # Кирилл, 16 годиков, ходит на 3-е чаепитие подряд
        self.players = {}
        self.playersAlive = 0
        self.playersEndedRound = 0
        self.handlers = []

        self.lastPlayerId = -1
        self.started = False
        self.prices = {'materials': [800, 650, 500, 400, 300],
                       'products': [6500, 6000, 5500, 5000, 4500]}
        self.requestsProduce = {}
        self.requestsMaterials = {}
        self.requestsProducts = {}
        self.requestsFactories = {}
        self.thingToSell()

        self.buildingFactories = {}
        self.factories = {}

    def start_game(self):
        self.started = True
        self.channel.send({'type': 'game_started', 'data': ''})
        self.startNewRound()

    def updateGameLevel(self):
        gameLevelThisThing = self.gameLevelUpdateTable[self.gameLevel - 1]
        newGameLevel = choice(gameLevelThisThing)
        self.gameLevel = newGameLevel

    def getPlayersInfo(self):
        all_info = {}
        for key in self.players.keys():
            info = self.players[key].getInfo()
            info['game_lvl'] = self.gameLevel
            all_info[key] = info
        return all_info

    def add_new_player(self):
        if self.slots >= self.playersAlive:
            raise Exception('Players limit')
        self.lastPlayerId += 1
        self.playersAlive += 1
        player = Player(str(self.lastPlayerId))
        self.players[str(self.lastPlayerId)] = player
        self.factories[str(self.lastPlayerId)] = []
        return player

    def payTaxes(self):
        for key in self.players.keys():
            if self.players[key].payTaxes():
                self.playersAlive -= 1

    def findLameDucks(self):
        new_players = {}
        for key in self.players.keys():
            if not self.players[key].isDead:
                new_players[key] = self.players[key]
            else:
                self.playersAlive -= 1
        self.players = new_players

    def killPlayer(self, player_id):
        new_players = {}
        for key in self.players.keys():
            if player_id != key:
                new_players[key] = self.players[key]
            else:
                self.playersAlive -= 1
        self.players = new_players

    def checkForGameEnd(self):
        if self.playersAlive == 1:
            for key in self.players.keys():
                if not self.players[key].isDead:
                    return key
        if all(list(map(lambda x: x.isDead, self.players.values()))):
            return 'NO ONE'
        return False

    def thingToSell(self):
        self.thingsToSell = {}
        self.thingsToSell['materials'] = int(0.5 * (self.gameLevel + 1)) * self.playersAlive
        self.thingsToSell['products'] = int((7 - self.gameLevel) * 0.5) * self.playersAlive

    def playerEndTurn(self):
        self.playersEndedRound += 1
        if self.playersEndedRound == self.playersAlive:
            self.produce()
            self.handlingRequestsMaterial()
            self.handlingRequestsProduct()
            self.handlingRequestsFactories()
            self.payTaxes()
            self.startNewRound()
            return True
        return False

    def newRequestFactory(self, player_id, count):
        self.requestsFactories[player_id] = count
        return True

    def newRequestProduce(self, player_id, materials):
        if materials > self.players[player_id].materials and materials <= self.players[player_id].factories:
            return False
        self.requestsProduce[player_id] = materials
        return True

    def newRequestMaterial(self, player_id, count, price):
        if self.prices['materials'][self.gameLevel - 1] > price:
            return False
        self.requestsMaterials[player_id] = [price, count]
        return True

    def newRequestProduct(self, player_id, count, price):
        if self.prices['products'][self.gameLevel - 1] < price:
            return False
        self.requestsProducts[player_id] = [price, count]
        return True

    def cheatSetValue(self, player_id, thing_type, value):
        setattr(self.players[player_id], thing_type, value)

    def startNewRound(self):
        self.channel.send({'type': 'new_round_started', 'data': ''})
        self.buildSomeFactory()
        self.requestsProduce = {}
        self.requestsMaterials = {}
        self.requestsProducts = {}
        self.requestsFactories = {}
        self.playersEndedRound = 0
        self.updateGameLevel()
        self.thingToSell()
        for player_id in self.players:
            self.players[player_id].turn = True

    def produce(self):
        for key in self.requestsProduce.keys():
            request = self.requestsProduce[key]
            self.players[key].materials -= request
            self.players[key].products += request
            self.players[key].money -= 2000 * request

    def buildSomeFactory(self):
        for key in self.buildingFactories.keys():
            factories = self.buildingFactories[key]
            new_factories = []
            for i in range(len(factories)):
                if not factories[i].grow():
                    new_factories.append(factories[i])
                else:
                    self.players[key].factories += 1
            self.buildingFactories[key] = new_factories

    def handlingRequestsMaterial(self):
        requests = list(zip(self.requestsMaterials.keys(), self.requestsMaterials.values()))
        requests.sort(key=lambda x: x[1][0])
        requests.reverse()
        th = self.thingsToSell['materials']
        while True:
            if requests == [] or th == 0:
                break
            request = requests.pop(0)
            sellCount = min(th, request[1][1])
            price = request[1][0]
            th -= sellCount
            self.players[request[0]].money -= sellCount * price
            self.players[request[0]].materials += sellCount
            print(self.players[request[0]].id, sellCount)

    def handlingRequestsProduct(self):
        requests = list(zip(self.requestsProducts.keys(), self.requestsProducts.values()))
        requests.sort(key=lambda x: x[1][0])
        th = self.thingsToSell['products']
        while True:
            if requests == [] or th == 0:
                break
            request = requests.pop(0)
            sellCount = min(th, request[1][1])
            price = request[1][0]
            th -= sellCount
            self.players[request[0]].money += sellCount * price
            self.players[request[0]].products -= sellCount

    def handlingRequestsFactories(self):
        requests = list(zip(self.requestsFactories.keys(), self.requestsFactories.values()))
        while True:
            if requests == []:
                break
            request = requests.pop(0)
            owner = request[0]
            self.buildingFactories[owner] = self.buildingFactories.get(owner, [])
            for i in range(request[1]):
                self.buildingFactories[owner].append(Factory(owner))
            self.players[owner].money -= 2500 * request[1]

        ##
