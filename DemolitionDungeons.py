# Demolition Dungeons
# made by Gus Gurley

from cmu_112_graphics import *

import math

# https://docs.python.org/3/library/pickle.html
import pickle

# https://www.geeksforgeeks.org/python-list-files-in-a-directory/
import os

class Game():
    def __init__(self, player1, player2):
        self.curAlly = player1
        self.curEnemy = player2
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
        self.turnCount += 1
        self.curAlly, self.curEnemy = self.curEnemy, self.curAlly

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
        self.resources = {"Gold":10000000}

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
        enemyEnterance = None

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
            enemyEntrance.enemyRegiment == None

        allyInHomeBase = selfEntrance.allyRegiment
        selfEntrance.allyRegiment = Regiment(tempReg).merge(allyInHomeBase)
        selfEntrance.allyRegiment.onAllySide = True

    def warpToEnemy(self, enemyPlayer):
        selfEntrance = None
        enemyEnterance = None

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
            selfEntrance.allyRegiment == None

        allyInEnemyBase = enemyEntrance.enemyRegiment
        enemyEntrance.enemyRegiment = Regiment(tempReg).merge(allyInEnemyBase)
        enemyEntrance.enemyRegiment.onAllySide = False
    
    def checkRuins(self):
        for row in self.buildings:
            for building in row:
                if (not type(building) == Ruin and not building == None and
                    not type(building) == Entrance):
                    if building.health <= 0:
                        building = Ruin()

class Building():
    def __init__(self):
        self.allyRegiment = None
        self.enemyRegiment = None
        self.traps = []
        self.health = 300

    def __repr__(self):
        return f'{self.name}'

class Ruin(Building):
    def __init__(self):
        super().__init__()
        self.name = "Ruin"
        self.health = 0

class Entrance(Building):
    def __init__(self):
        super().__init__()
        self.name = "Entrance"
        self.health = 0

class GoldMine(Building):
    def __init__(self):
        super().__init__()
        self.name = "GoldMine"
        # "assets/goldMine.png"
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
        name=f"{self.name}: {self.attack}, {self.curHealth}, {self.curMovement}"
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
        if enemyRegiment == None:
            if not self.onAllySide:
                room.health -= self.attack
            return False
        
        for troop in self.troops:
            troop.attackAction(room, enemyRegiment)

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

class Trap():
    def __init__(self):
        pass

    def __repr__(self):
        return f'{self.name}'

class Bomb(Trap):
    def __init__(self):
        self.cost = ("Gold", 10)
        self.name = "Bomb"
    
    def trip(self, buildings, roomCords, room, regiment):
        for troop in regiment.troops:
            troop.curHealth -= 25
        regiment.cleanOutDead(room)
        room.traps.remove(self)

class Button():
    def __init__(self, x0, y0, x1, y1, text, action = None):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.text = text
        self.action = action
    
    def checkClicked(self, mouseX, mouseY):
        return self.x0 <= mouseX <= self.x1 and self.y0 <= mouseY <= self.y1

    def onClick(self):
        if self.action != None:
            self.action()

def appStarted(app):

    # scale is the n by n pixel dimmensions of one room
    app.scale = 100

    app.cameraY = 50
    app.cameraX = 0
    app.font = "Century 14 bold"

    # add save and load segment
    app.game = makeNewGame(app)
    app.sameSide = True
    app.troopMove = None
    
    app.needsTarget = None

    app.images = loadImages(app)
    app.UI = loadGameUI(app)
    app.curBoard = app.game.curAlly.buildings

def getSaves():
        path = "saves/"
        files = os.listdir(path)
        return files

def saveGame(game, fileName):
    file = open(fileName, "wb")
    pickle.dump(game, file)
    file.close()

def loadGame(fileName):
    file = open("saves/" + fileName, "rb")
    game = pickle.load(file)
    file.close()
    return game    

def loadImages(app):
    result = {}
    #https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.pngitem.com%2Fmiddle
    #%2FimJJomh_gold-mine-clipart-hd-png-download%2F&psig=AOvVaw0mTltkyz9li1IQg
    #KUujKYi&ust=1669686072855000&source=images&cd=vfe&ved=0CA8QjRxqFwoTCJCFy
    #rzfz_sCFQAAAAAdAAAAABAD
    result["GoldMine"] = app.loadImage("assets/goldMine.jpeg")
    #https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.vectorstock.com%2Fro
    #yalty-free-vector%2Fcartoon-mine-entrance-retro-tunnel-old-mine-vector-331
    #46747&psig=AOvVaw3wiEwEOKoBuPDwC3X5n2q9&ust=1669686129161000&source=images
    #&cd=vfe&ved=0CA8QjRxqFwoTCOi0k93fz_sCFQAAAAAdAAAAABAD
    result["Entrance"] = app.loadImage("assets/entrance.jpeg")
    #https://www.google.com/url?sa=i&url=https%3A%2F%2Fen.wiktionary.org%2Fwiki
    #%2Fsquare&psig=AOvVaw3p3TqKymy4hBryA073nkcs&ust=1669686202053000&source=im
    #ages&cd=vfe&ved=0CA8QjRxqFwoTCMDivPrfz_sCFQAAAAAdAAAAABAD
    result["Empty"] = app.loadImage("assets/none.png")
    #https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.flaticon.com%2Ffree-
    #icon%2Fbarracks_3016501&psig=AOvVaw0L6R8z3SDMCLmx9qWnZ60g&ust=166975403737
    #3000&source=images&cd=vfe&ved=0CA8QjRxqGAoTCPCR0uPc0fsCFQAAAAAdAAAAABDpAg
    result["Barracks"] = app.loadImage("assets/barracks.png")
    #https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.nicepng.com%2Fourpic
    #%2Fu2y3q8u2e6o0i1o0_environmental-clipart-green-brain-manufacturing-clipar
    #t-png%2F&psig=AOvVaw3ureIqIOTmHA_mC2SWgYU0&ust=1669754191901000&source=ima
    #ges&cd=vfe&ved=0CA8QjRxqFwoTCMCZzavd0fsCFQAAAAAdAAAAABAD
    result["Factory"] = app.loadImage("assets/factory.jpeg")
    #https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.kindpng.com%2Ffree%2
    #Fruins%2F&psig=AOvVaw1dmkCeCk4c5k-Qpa5DCsiP&ust=1669841646321000&source=im
    #ages&cd=vfe&ved=0CA8QjRxqFwoTCLid0oOj1PsCFQAAAAAdAAAAABAD
    result["Ruins"] = app.loadImage("assets/ruins.jpeg")
    return result

def loadGameUI(app):
    result = []
    result.append(Button(10, app.height - 50, 90, app.height - 10,
                        "End Turn", app.game.endTurn))
    if app.sameSide:
        result.append(Button(app.width - 120, app.height - 50, app.width - 10,
                    app.height - 10, "Go To Enemy", lambda: switchSides(app)))
    else:
        result.append(Button(app.width - 120, app.height - 50, app.width - 10,
                    app.height - 10, "Return Home", lambda: switchSides(app)))
    return result

def switchSides(app):
    app.sameSide = not app.sameSide
    app.UI = loadGameUI(app)
    update(app)

def makeNewGame(app):
    # player1Name = app.getUserInput("Enter Player One Name")
    player1 = Player("gus")
    # player2Name = app.getUserInput("Enter Player Two Name")
    player2 = Player("sug")

    return Game(player1, player2)

def keyPressed(app, event):
    app.UI = loadGameUI(app)
    if event.key == "Down":
        app.cameraY -= app.scale
    if event.key == "Up":
        app.cameraY += app.scale
    if event.key == "Right":
        app.cameraX -= app.scale
    if event.key == "Left":
        app.cameraX += app.scale
    if event.key == "p":
        app.scale *= 1.1
    if event.key == "o":
        app.scale /= 1.1
    
    app.scale = min(app.scale, 300)
    maxScale = max(app.width/len(app.curBoard[0]),
        app.height/len(app.curBoard))
    app.scale = max(app.scale, maxScale)
    app.scale = round(app.scale)
    app.cameraX = min(app.cameraX, 0)
    app.cameraY = min(app.cameraY, 50)
    app.cameraX = max(app.cameraX, app.width - len(app.curBoard[0])*app.scale)
    app.cameraY = max(app.cameraY, app.height - len(app.curBoard)*app.scale)

    print(app.cameraY, app.cameraX, app.scale)

def purcahseBuildingsList(app, row, col):
    app.UI.append(Button(20, 60, 100, 100, "GoldMine",
        lambda: app.game.curAlly.purchase((row,col), GoldMine())))
    app.UI.append(Button(20, 120, 100, 160, "Barracks",
        lambda: app.game.curAlly.purchase((row,col), Barracks())))
    app.UI.append(Button(20, 180, 100, 220, "Factory",
        lambda: app.game.curAlly.purchase((row,col), Factory())))

def purchaseTroopList(app, room):
    app.UI.append(Button(20, 60, 100, 100, "Soldier",
        lambda: room.buildTroop(app.game.curAlly.resources, Soldier())))

def purchaseTrapList(app, room):
    app.UI = loadGameUI(app)
    app.UI.append(Button(20, 60, 100, 100, "Bomb", target(app,
        lambda target: room.buildTrap(app.game.curAlly.resources, Bomb(),
        app.curBoard[target[0]][target[1]]))))

def target(app, action):
    def help():
        app.UI.append(Button(20,60,120,120,"Select Room\nto Target"))
        app.needsTarget = action
    return help

# def move(app, room, roomCord):
#     app.UI = loadGameUI(app)
#     if app.sameSide:
#         regi = room.allyRegiment
#     else:
#         regi = room.enemyRegiment
#     app.UI.append(Button(20, 60, 100, 100, "Move", target(app,
#     lambda target: room.allyRegiment.move(roomCord, target, app.curBoard))))

def attack(app, room):
    if app.sameSide:
        room.allyRegiment.attack(room, room.enemyRegiment)
        app.game.curAlly.checkRuins()
    else:
        room.enemyRegiment.attack(room, room.allyRegiment)
        app.game.curEnemy.checkRuins()

def myRoomActions(app, room, roomCords):
    if not room.allyRegiment == None:
        app.UI.append(Button(20, 120, 100, 160, "Move", target(app,
    lambda target: room.allyRegiment.move(roomCords, target, app.curBoard))))
        app.UI.append(Button(20, 180, 100, 220, "Attack!",
            lambda: attack(app, room)))

    if type(room) == Barracks:
        if not room.madeTroopThisTurn:
            app.UI.append(Button(20, 60, 100, 100, "Recruit", 
                lambda: purchaseTroopList(app, room)))
        else:
            app.UI.append(Button(20, 60, 100, 100, "Used"))
    
    if type(room) == Factory:
        if not room.madeTrapThisTurn:
            app.UI.append(Button(20, 60, 100, 100, "Build", 
            lambda: purchaseTrapList(app, room)))
        else:
            app.UI.append(Button(20, 60, 100, 100, "Used"))

    if type(room) == Entrance and not room.allyRegiment == None:
            app.UI.append(Button(20, 60, 100, 100, "Warp",
            lambda: app.game.curAlly.warpToEnemy(app.game.curEnemy)))
                

def theirRoomActions(app, room, roomCords):
    if not room.enemyRegiment == None:
        app.UI.append(Button(20, 120, 100, 160, "Move", target(app,
    lambda target: room.enemyRegiment.move(roomCords, target, app.curBoard))))
        app.UI.append(Button(20, 180, 100, 220, "Attack!",
            lambda: attack(app, room)))
    
    if type(room) == Entrance and not room.enemyRegiment == None:
        app.UI.append(Button(20, 60, 100, 100, "Warp",
            lambda: app.game.curAlly.warpHome(app.game.curEnemy)))

def showMyInsides(app, room):
    allyTroops = "Allies: "
    enemyTroops = "Enemies: "
    traps = "Traps: "
    if room.allyRegiment != None:
        for troop in room.allyRegiment.troops:
            allyTroops += f"{troop}\n"
    if room.enemyRegiment != None:
        for troop in room.enemyRegiment.troops:
            enemyTroops += f"{troop}\n"
    for trap in room.traps:
        traps += f"{trap.name}\n"

    if allyTroops == "Allies: ":
        allyTroops += "None \n"
    if enemyTroops == "Enemies: ":
        enemyTroops += "None \n"
    if traps == "Traps: ":
        traps += "None \n"
    info = allyTroops + enemyTroops + traps

    app.UI.append(Button(app.width-210, 60, app.width-10, 360, info))

def showTheirInsides(app, room):
    allyTroops = "Allies: "
    enemyTroops = "Enemies: "
    if room.enemyRegiment != None:
        for troop in room.enemyRegiment.troops:
            allyTroops += f"{troop}\n"
    if room.allyRegiment != None:
        for troop in room.allyRegiment.troops:
            enemyTroops += f"{troop}\n"
    
    if allyTroops == "Allies: ":
        allyTroops += "None \n"
    if enemyTroops == "Enemies: ":
        enemyTroops += "None \n"
    info = allyTroops + enemyTroops

    app.UI.append(Button(app.width-210, 60, app.width-10, 360, info))

def mousePressed(app, event):
    for button in app.UI:
        if button.checkClicked(event.x, event.y):
            app.UI = loadGameUI(app)
            button.onClick()
            update(app)
            return

    boardCol = math.floor((event.x - app.cameraX) / app.scale)
    boardRow = math.floor((event.y - app.cameraY) / app.scale)
    if (boardCol >= 0 and boardCol < len(app.curBoard[0]) and
        boardRow >= 0 and boardRow < len(app.curBoard)):
        app.UI = loadGameUI(app)
        if (app.sameSide and 
            app.game.curAlly.isContructionZone(boardRow, boardCol)):
            x0 = (boardCol * app.scale) + app.cameraX
            y0 = (boardRow * app.scale) + app.cameraY
            app.UI.append(Button(x0, y0, x0 + app.scale, y0 + app.scale, "Buy?",
                lambda: purcahseBuildingsList(app, boardRow, boardCol)))
            return
        room = app.curBoard[boardRow][boardCol]
        if not app.needsTarget == None:
            app.needsTarget((boardRow, boardCol))
            app.needsTarget = None

        # if (app.sameSide and not app.troopMove == None):
        #     go = app.game.curAlly.buildings[app.troopMove[0]][app.troopMove[1]]
        #     go.allyRegiment.move(app.troopMove, (boardRow, boardCol),
        #          app.game.curAlly.buildings)
        #     update(app)
        #     app.troopMove = None
        #     return
        # elif (not app.sameSide and not app.troopMove == None):
        #     go = app.game.curEnemy.buildings[app.troopMove[0]][app.troopMove[1]]
        #     go.enemyRegiment.move(app.troopMove, (boardRow, boardCol),
        #          app.game.curEnemy.buildings)
        #     update(app)
        #     app.troopMove = None
        #     return

        if (app.sameSide and room != None):
            myRoomActions(app, room, (boardRow, boardCol))
            showMyInsides(app, room)
        elif (not app.sameSide and room != None):
            theirRoomActions(app, room, (boardRow, boardCol))
            showTheirInsides(app, room)

def update(app):
    if app.sameSide:
        app.curBoard = app.game.curAlly.buildings
    else:
        app.curBoard = app.game.curEnemy.buildings

def drawRoom(app, canvas, row, col, room):
    if room == None:
        roomImage = app.images["Empty"]
    else:
        roomImage = app.images[room.name]
    imageWidth, imageHeight = roomImage.size
    roomImage = app.scaleImage(roomImage, app.scale/imageWidth)
    x = (col * app.scale) + app.cameraX
    y = (row * app.scale) + app.cameraY
    canvas.create_image(x + (app.scale / 2), y + (app.scale / 2),
        image=ImageTk.PhotoImage(roomImage))

def drawMap(app, canvas):
    for row in range(len(app.curBoard)):
        for col in range(len(app.curBoard[0])):
            drawRoom(app, canvas, row, col, app.curBoard[row][col])
        
def drawUI(app, canvas):
    for button in app.UI:
        canvas.create_rectangle(button.x0, button.y0, button.x1, button.y1,
        fill = "black", outline = "blue",width = 5)
        canvas.create_text(button.x0 + (button.x1 - button.x0)/2, (button.y0 + 
            (button.y1 - button.y0)/2), text = button.text, font = app.font)

def drawResources(app, canvas):
    result = app.game.curAlly.name
    result += f" Turn {app.game.turnCount // 2}   "
    for key in app.game.curAlly.resources:
        result += f"{key} : {app.game.curAlly.resources[key]}   "
    canvas.create_rectangle(0, 0, app.width, 50, fill = "gray", width = 0)
    canvas.create_text(app.width / 2, 25, text = result, font = app.font)

def redrawAll(app, canvas):
    drawMap(app, canvas)
    drawUI(app, canvas)
    drawResources(app, canvas)

runApp(width = 800, height = 800)