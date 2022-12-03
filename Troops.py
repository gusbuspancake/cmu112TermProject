

class Troop():
    def __init__(self, attack, health, movement, size, cost = ("Gold", 0)):
        self.attack = attack
        self.hasAttacked = True
        self.maxHealth = health
        self.curHealth = health
        self.maxMovement = movement
        self.curMovement = 0
        self.cost = cost
        self.size = size
    
    def __repr__(self):
        name = (f"{self.name}: AK:{self.attack}, " +
        f"HP:{self.curHealth}/{self.maxHealth}, " +
        f"MV{self.curMovement}/{self.maxMovement}")
        return name

class Soldier(Troop):
    def __init__(self):
        super().__init__(attack = 10, health = 35, movement = 5, size = 5,
            cost = ("Gold", 50))
        self.name = "Soldier"

    # soldiers attack the enemy troop with the largest size in the same room
    def attackAction(self, room, enemyRegiment):
        if self.hasAttacked:
            return
        
        biggestEnemy = None
        biggestEnemySize = -999
        for troop in enemyRegiment.troops:
            if troop.size > biggestEnemySize:
                biggestEnemy = troop
                biggestEnemySize = troop.size
            elif troop.size == biggestEnemySize:
                if troop.curHealth > biggestEnemy.curHealth:
                    biggestEnemy = troop
                    biggestEnemySize = troop.size
        biggestEnemy.curHealth -= self.attack
        enemyRegiment.cleanOutDead(room)

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

    def attack(self, room, enemyRegiment):
        if enemyRegiment == None and self.onAllySide:
            return False

        roomDamage = 0 
        
        for troop in self.troops:
            if enemyRegiment == None:
                roomDamage = troop.attack
            else:
                troop.attackAction(room, enemyRegiment)

        if enemyRegiment == None and not self.onAllySide:
            room.health -= roomDamage

    def cleanOutDead(self, room):
        for troop in self.troops:
            if troop.curHealth <= 0:
                self.troops.remove(troop)

        if len(self.troops) == 0:
            # self = None, i want this to work
            if self.onAllySide:
                room.allyRegiment = None
            else:
                room.enemyRegiment = None

    # merges current regiment to regiment at final destination if one exist
    # returns new conjoioned regiment
    def merge(self, other):
        if other == None:
            return self
        else:
            return Regiment(other.troops + self.troops, other.onAllySide)

    def move(self, startCord, finishCord, buildings):
        if self.getCurMovement() == 0:
            return
        path = self.movePath(startCord, finishCord, buildings)
        path.pop(0)
        curRoom = buildings[startCord[0]][startCord[1]]
        # might delete this later
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
