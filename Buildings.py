
from Troops import Regiment

class Building():
    def __init__(self):
        self.allyRegiment = None
        self.enemyRegiment = None
        self.traps = []
        self.health = 100

    def __repr__(self):
        return f'{self.name}'

class Ruin(Building):
    def __init__(self, oldBuilding):
        super().__init__()
        self.name = "Ruin"
        self.health = 0
        self.debt = ("Gold", 100)
        self.allyRegiment = oldBuilding.allyRegiment
        self.enemyRegiment = oldBuilding.enemyRegiment
        self.traps = oldBuilding.traps

class Entrance(Building):
    def __init__(self):
        super().__init__()
        self.name = "Entrance"
        self.health = 0

class GoldMine(Building):
    def __init__(self):
        super().__init__()
        self.name = "GoldMine"
        self.cost = ("Gold", 200)
        self.profit = ("Gold", 50)

class Barracks(Building):
    def __init__(self):
        super().__init__()
        self.name = "Barracks"
        self.cost = ("Gold", 100)
        self.madeTroopThisTurn = False

    def buildTroop(self, resources, troop):
        if self.madeTroopThisTurn:
            return False
        currResourceType = resources[troop.cost[0]]
        if currResourceType < troop.cost[1]:
            return False
        self.madeTroopThisTurn = True
        tempReg = Regiment([troop])
        self.allyRegiment = tempReg.merge(self.allyRegiment)

        resources[troop.cost[0]] -= troop.cost[1]    

class Factory(Building):
    def __init__(self):
        super().__init__()
        self.name = "Factory"
        self.cost = ("Gold", 100)
        self.madeTrapThisTurn = False

    def buildTrap(self, resources, trap, targetRoom):
        if self.madeTrapThisTurn:
            return False
        currResourceType = resources[trap.cost[0]]
        if currResourceType < trap.cost[1]:
            return False
        self.madeTrapThisTurn = True
        targetRoom.traps.append(trap)

        resources[trap.cost[0]] -= trap.cost[1]  
