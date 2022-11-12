# Demolition Dungeons
# made by Gus Gurley

from cmu_112_graphics import *

class Player():
    def __init__(self):
        self.buildings = []
        self.buildings.insert(0, Entrance(self))
        self.resources = {"gold":500}

    # helper function for debugging before GUI
    def printBuildings(self):
        for i in range(len(self.buildings)):
            building = self.buildings[i]
            print(i, building.name, building.adjacent)     

    def endTurn(self):
        for building in self.buildings:
            if type(building) == GoldMine:
                self.resources["gold"] += 50

    def getConstructionZones(self):
        result = dict()
        for i in range(len(self.buildings)):
            building = self.buildings[i]
            if type(building) == Construction:
                result[building] = i
        return result

    def canPurchase(self, building):
        currResourceType = self.resources[building.cost[0]]
        return not currResourceType < building.cost[1]
    
    #construction index comes from dictinoary in get construction zones function
    def upgrade(self, constructionIndex, upgradeBuilding):
        # can you purchase this building?
        if not canPurchase(upgradeBuilding):
            return False

        # Replaces contruction zone with new building of same adjacency index
        currentZone = self.buildings[constructionIndex]
        upgradeBuilding.adjacent = currentZone.adjacent
        self.buildings[constructionIndex] = upgradeBuilding

        # make new construction zones
        for index in range(len(upgradeBuilding.adjacent)):
            if upgradeBuilding.adjacent[index] == None:
                newConstructionIndex = len(self.buildings)
                upgradeBuilding.adjacent[index] = newConstructionIndex
                self.buildings.append(Construction(index, constructionIndex))
    
# class Building():
#     def __init__(self, base):
#         self.name = ""
#         self.allyTroops = []
#         self.enemyTroops = []

#         #0:up, 1:right, 2:down, 3:left
#         self.adjacent = [None, None, None, None]

class Entrance(): # make building superclass
    def __init__(self, player):
        self.name = "Entrance"
        # refers to 4 construction zones necessary to start game
        self.adjacent = [1,2,3,4]
        for i in range(4):
            player.buildings.append(Construction(i, 0))

class Construction(): # make building superclass
    def __init__(self, oldPos, oldIndex):
        self.name = "Construction"
        self.adjacent = [None, None, None, None]
        self.adjacent[oldPos-2] = oldIndex
    
    def __repr__(self):
        return f'{self.name}'

class GoldMine(): # make building superclass
    def __init__(self):
        self.name = "Goldmine"
        self.cost = ("gold", 200)


gus = Player()
print(gus.getConstructionZones())