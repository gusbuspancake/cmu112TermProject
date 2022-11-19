# Demolition Dungeons
# made by Gus Gurley

from cmu_112_graphics import *


class Player():
    def __init__(self):
        self.buildings = [[None,None,None],[None,None,None],[None,None,None]]
        self.buildings[1][1] = Entrance()
        self.resources = {"gold":10000000}

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
                    # https://www.geeksforgeeks.org/python-inner-functions/
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
    def __init__(self):
        self.allyRegiment = None
        self.enemyRegiment = None
        self.traps = []
        self.health = 300

    def __repr__(self):
        return f'{self.name}'

class Entrance(Building):
    def __init__(self):
        super().__init__()
        self.name = "Entr"

class GoldMine(Building):
    def __init__(self):
        super().__init__()
        self.name = "Gold"
        self.cost = ("gold", 200)

class Barracks(Building):
    def __init__(self):
        super().__init__()
        self.name = "Barracks"
        self.cost = ("gold", 100)
    
    # def buildTroop(troop):

class Factory(Building):
    def __init__(self):
        super().__init__()
        self.name = "Factory"
        self.cost = ("gold", 100)

    # def buildTrap(trap):

class Troop():
    def __init__(self, attack, health, movement, size, cost = ("gold", 0)):
        self.attack = attack
        self.maxHealth = health
        self.curHealth = health
        self.maxMovement = movement
        self.curMovement = movement
        self.cost = cost
        self.size = size
    
    def __repr__(self):
        return f'{self.name}'

class Soldier(Troop):
    def __init__(self):
        super().__init__(attack = 10, health = 35, movement = 5, size = 5,
            cost = ("gold", 50))
        self.name = "Soldier"

class Regiment():
    def __init__(self, troops, onAllySide = True):
        self.troops = troops
        self.onAllySide = onAllySide

    def getCurMovement(self):
        curMovement = self.troops[0].curMovement
        for troop in self.troops:
            if troop.curMovement < curMovement:
                curMovement = troop.curMovement
        return curMovement

    def getSize(self):
        size = 0
        for troop in self.troops:
            size += troop.size
        return size

    def cleanOutDead(self):
        for troop in self.troops:
            if troop.curHealth <= 0:
                self.troops.remove(troop)

    # merges current regiment to regiment at final destination if one exist
    # returns new conjoioned regiment
    def merge(self, other):
        if other == None:
            return self
        else:
            return Regiment(other.troops + self.troops, other.onAllySide)

    def move(self, startCord, finishCord, buildings):
        path = self.movePath(startCord, finishCord, buildings)
        curRoom = buildings[startCord[0]][startCord[1]]
        if self.onAllySide:
            curRoom.allyRegiment = None
        else:
            curRoom.enemyRegiment = None
        for roomCord in path:
            curRoom = buildings[roomCord[0]][roomCord[1]]
            for troop in self.troops:
                troop.curMovement -= 1
            if not self.onAllySide:
                for trap in curRoom.traps:
                    trap.trip(buildings, roomCord, curRoom, self)
            if self.getCurMovement() == 0:
                break
            if not curRoom.enemyRegiment == None:
                if curRoom.enemyRegiment.getSize() >= self.getSize():
                    break
        if self.onAllySide:
            curRoom.allyRegiment = self.merge(curRoom.allyRegiment)
        else:
            curRoom.enemyRegiment = self.merge(curRoom.enemyRegiment)

    # https://www.geeksforgeeks.org/a-search-algorithm/
    def movePath(self, startCord, finishCord, buildings):
        openDict = {startCord: 0}
        closedDict = {}

        def manhattanDist(cord1, cord2):
            return abs(cord1[0] - cord2[0]) + abs(cord1[1] - cord2[1])
        
        while not len(openDict) == 0:
            
            # find elm with smallest manhattanDist and remove from openList
            smallestCord = (0,0)
            smallestValue = len(buildings)**2
            for key in openDict:
                if openDict[key] < smallestValue:
                    smallestCord = key
                    smallestValue = openDict[key]

            curCord = smallestCord
            curValue = smallestValue
            
            del openDict[curCord]
            possibleMoves = [(0,1), (0,-1), (1,0), (-1,0)]
            for move in possibleMoves:
                newCord = (curCord[0] + move[0], curCord[1] + move[1])
                # if orthogonal move is a wall, continue
                if buildings[newCord[0]][newCord[1]] == None:
                    continue
                if newCord == finishCord:
                    return list(closedDict.keys()) + [curCord, newCord]
                newValue = (manhattanDist(newCord, curCord) + 
                                manhattanDist(newCord, finishCord))

                if newCord in openDict:
                    if openDict[newCord] <= newValue:
                        continue
                        
                if newCord in closedDict:
                    if closedDict[newCord] <= newValue:
                        continue
                

                openDict[newCord] = newValue

            closedDict[curCord] = curValue
        print("movePath is broken")
        return False     


class Trap():
    def __init__(self):
        pass

    def __repr__(self):
        return f'{self.name}'

class Bomb(Trap):
    def __init__(self):
        self.cost = ("gold", 10)
        self.name = "Bomb"
    
    def trip(self, buildings, roomCords, room, regiment):
        for troop in regiment.troops:
            troop.curHealth -= 25
        regiment.cleanOutDead()
        room.traps.remove(self)

gus = Player()
gus.purchase((1,2), GoldMine())
gus.purchase((1,3), GoldMine())
gus.purchase((1,4), GoldMine())
gus.purchase((2,4), GoldMine())
gus.purchase((3,4), GoldMine())
gus.purchase((3,3), GoldMine())
gus.purchase((3,2), GoldMine())

gus.buildings[1][1].enemyRegiment = Regiment([Soldier(),Soldier()], False)

print(gus.buildings[1][1].enemyRegiment.troops)
gus.printBuildings()

gus.buildings[1][3].traps.append(Bomb())
gus.buildings[1][1].enemyRegiment.move((1,1),(3,2),gus.buildings)

print(gus.buildings[2][4].enemyRegiment.troops[0].curHealth)

print(gus.buildings[1][3].traps)