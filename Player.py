
from Buildings import Entrance, Ruin

from Troops import Regiment

class Player():
    def __init__(self, name):
        self.name = name
        self.buildings = []
        for i in range(11):
            temp = []
            for j in range(11):
                temp.append(None)
            self.buildings.append(temp)
        
        self.buildings[5][5] = Entrance()
        self.resources = {"Gold":200}

    # helper function for debugging before GUI
    def printBuildings(self):
        for row in self.buildings:
            print(row)  

    def isContructionZone(self, row, col):
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
                return True
        return False

    def canPurchase(self, building):
        currResourceType = self.resources[building.cost[0]]
        return not currResourceType < building.cost[1]
    
    # zoneIndex is tuple of (row,col) in buildings
    # building is the building to pruchase
    def purchase(self, zoneIndex, building):
        # can you purchase this building?
        if not self.canPurchase(building):
            return False
        self.buildings[zoneIndex[0]][zoneIndex[1]] = building
        self.resources[building.cost[0]] -= building.cost[1]
        
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

    def warpHome(self, enemyPlayer):
        selfEntrance = None
        enemyEntrance = None

        for row in self.buildings:
            for building in row:
                if type(building) == Entrance:
                    selfEntrance = building
                    break
        
        for row in enemyPlayer.buildings:
            for building in row:
                if type(building) == Entrance:
                    enemyEntrance = building
                    break
        
        tempReg = []
        for troop in enemyEntrance.enemyRegiment.troops:
            if troop.curMovement == troop.maxMovement:
                troop.curMovement = 0
                tempReg.append(troop)
                enemyEntrance.enemyRegiment.troops.remove(troop)
        
        if len(enemyEntrance.enemyRegiment.troops) == 0:
            enemyEntrance.enemyRegiment = None

        allyInHomeBase = selfEntrance.allyRegiment
        selfEntrance.allyRegiment = Regiment(tempReg).merge(allyInHomeBase)
        selfEntrance.allyRegiment.onAllySide = True

    def warpToEnemy(self, enemyPlayer):
        selfEntrance = None
        enemyEntrance = None

        for row in self.buildings:
            for building in row:
                if type(building) == Entrance:
                    selfEntrance = building
                    break
        
        for row in enemyPlayer.buildings:
            for building in row:
                if type(building) == Entrance:
                    enemyEntrance = building
                    break
        
        tempReg = []
        for troop in selfEntrance.allyRegiment.troops:
            if troop.curMovement == troop.maxMovement:
                troop.curMovement = 0
                tempReg.append(troop)
                selfEntrance.allyRegiment.troops.remove(troop)
        
        if len(selfEntrance.allyRegiment.troops) == 0:
            selfEntrance.allyRegiment = None

        allyInEnemyBase = enemyEntrance.enemyRegiment
        enemyEntrance.enemyRegiment = Regiment(tempReg).merge(allyInEnemyBase)
        enemyEntrance.enemyRegiment.onAllySide = False
    
    def checkRuins(self):
        for row in range(len(self.buildings)):
            for col in range(len(self.buildings[0])):
                building = self.buildings[row][col]
                if (not type(building) == Ruin and not building == None and
                    not type(building) == Entrance):
                    if building.health <= 0:
                        self.buildings[row][col] = Ruin(building)
