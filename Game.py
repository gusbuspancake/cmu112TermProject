
from Buildings import GoldMine, Barracks, Factory, Ruin

class Game():
    def __init__(self, player1, player2):
        self.curAlly = player1
        self.curEnemy = player2
        self.loser = None
        self.turnCount = 2

    def endTurn(self):
        for row in self.curAlly.buildings:
            for building in row:
                if building == None:
                    continue
                if type(building) == GoldMine:
                    self.curAlly.resources[building.profit[0]] += (
                        building.profit[1])
                elif type(building) == Barracks:
                    building.madeTroopThisTurn = False
                elif type(building) == Factory:
                    building.madeTrapThisTurn = False
                elif type(building) == Ruin:
                    self.curAlly.resources[building.debt[0]] -= (
                        building.debt[1])
                if not building.allyRegiment == None:
                    for troop in building.allyRegiment.troops:
                        troop.curMovement = troop.maxMovement
        for row in self.curEnemy.buildings:
            for building in row:
                if building == None:
                    continue
                if not building.enemyRegiment == None:
                    for troop in building.enemyRegiment.troops:
                        troop.curMovement = troop.maxMovement
                        troop.hasAttacked = False
        if self.curAlly.resources["Gold"] < 0:
            self.loser = self.curAlly
        self.turnCount += 1
        self.curAlly, self.curEnemy = self.curEnemy, self.curAlly
