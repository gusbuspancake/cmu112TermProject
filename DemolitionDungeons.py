# Demolition Dungeons
# made by Gus Gurley

from cmu_112_graphics import *


class Player():
    def __init__(self):
        self.buildings = [[None,None,None],[None,None,None],[None,None,None]]
        self.buildings[1][1] = Entrance(self, 0)
        self.resources = {"gold":500}
        self.nextId = 1

    # helper function for debugging before GUI
    def printBuildings(self):
        for row in self.buildings:
            print(row)  

    def endTurn(self):
        for building in self.buildings:
            if type(building) == GoldMine:
                self.resources["gold"] += 50

    # return a list of tuples of all available spaces to build
    def getConstructionZones(self):
        result = []
        for row in range(len(self.buildings)):
            for col in range(len(self.buildings[0])):
                building = self.buildings[row][col]
                if building == None:

                    # checks orthoganol spaces to see if they are buildings
                    def checkNone(buildings, row, col):
                        if (row<0 or col<0 or row>=len(buildings)
                            or col>=len(buildings[0])):
                            return False
                        return buildings[row][col] != None

                    if (checkNone(self.buildings, row+1, col) or 
                        checkNone(self.buildings, row-1, col) or
                        checkNone(self.buildings, row, col+1) or
                        checkNone(self.buildings, row, col-1)):
                        result.append((row, col))
        return result

    def canPurchase(self, building):
        currResourceType = self.resources[building.cost[0]]
        return not currResourceType < building.cost[1]
    
    # zoneIndex is tuple of (row,col) in buildings
    # pruchaseBuilding is the building to pruchase
    def purchase(self, zoneIndex, pruchaseBuilding):
        # can you purchase this building?
        if not self.canPurchase(pruchaseBuilding):
            return False
        self.buildings[zoneIndex[0]][zoneIndex[1]] = pruchaseBuilding
        
        self.expandMap(zoneIndex)

    def expandMap(self, zoneIndex):
        # checks if on top row
        if zoneIndex[0] == 0:
            newRow = []
            for i in range(len(self.buildings[0])):
                newRow.append(None)
            self.buildings.insert(0, newRow)

        # checks if on first col
        if zoneIndex[1] == 0:
            for row in self.buildings:
                row.insert(0, None)
        
        # checks if on bottom row
        if zoneIndex[0] == len(self.buildings) - 1:
            newRow = []
            for i in range(len(self.buildings[0])):
                newRow.append(None)
            self.buildings.append(newRow)
        
        # checks if on last col
        if zoneIndex[1] == len(self.buildings[0]) - 1:
            for row in self.buildings:
                row.append(None)
     
class Building():
    def __init__(self, id):
        self.id = id
        self.allyTroops = []
        self.enemyTroops = []
        self.traps = []
        self.health = 300

    def __repr__(self):
        return f'{self.name}'

class Entrance(Building):
    def __init__(self, id):
        super().__init__(id)
        self.name = "Entrance"

class GoldMine(Building):
    def __init__(self, id):
        super().__init__(id)
        self.name = "Goldmine"
        self.cost = ("gold", 200)

class Barracks(Building):
    def __init__(self, id):
        super().__init__(id)
        self.name = "Barracks"
        self.cost = ("gold", 100)
    
    # def buildTroop(troop):

class Troop():
    def __init__(self, attack, health, movement, cost):
        self.attack = attack
        self.maxHealth = health
        self.curHealth = health
        self.movement = movement
        self.cost = cost

    def move(self, startCord, finishCord, buidlings):
        # figure out maze finding thing
        pass

class Soldier(Troop):
    def __init__(self):
        super().__init__(attack = 10, health = 35, movement = 1,
            cost = ("gold", 50))

class Regiment(Troop):
    def __init__(self, troops):
        self.troops = troops



gus = Player()