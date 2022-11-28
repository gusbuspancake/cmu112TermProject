# Demolition Dungeons
# made by Gus Gurley

from cmu_112_graphics import *

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
        allyInHomeBase = Regiment(tempReg).merge(allyInHomeBase) 

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
        self.name = "Entrance"

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

    def buildTrap(self, resources, trap):
        if self.madeTrapThisTurn:
            return False
        currResourceType = resources[trap.cost[0]]
        if currResourceType < trap.cost[1]:
            return False
        self.madeTrapThisTurn = True
        self.traps.append(trap)

        resources[trap.cost[0]] -= trap.cost[1]  

class Troop():
    def __init__(self, attack, health, movement, size, cost = ("Gold", 0)):
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
            cost = ("Gold", 50))
        self.name = "Soldier"

    # soldiers attack the enemy troop with the largest size in the same room
    def attack(self, room, enemyRegiment):
        if enemyRegiment == None:
            return False
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
        path = self.movePath(startCord, finishCord, buildings)
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
    def __init__(self, x0, y0, x1, y1, text, action):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.text = text
        self.action = action
    
    def checkClicked(self, mouseX, mouseY):
        return self.x0 <= mouseX <= self.x1 and self.y0 <= mouseY <= self.y1

    def onClick(self):
        self.action()

def appStarted(app):

    # scale is the n by n pixel dimmensions of one room
    app.scale = 50

    # position of top left corner of the canvas in the map of buildings
    app.curRow = 0
    app.curCol = 0
    app.font = "Century 14 bold"

    # add save and load segment
    app.game = makeNewGame(app)

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
    return result

def loadGameUI(app):
    result = []
    result.append(Button(10, app.height - 50, 90, app.height - 10,
                        "End Turn", app.game.endTurn))
    return result

def makeNewGame(app):
    # player1Name = app.getUserInput("Enter Player One Name")
    player1 = Player("gus")
    # player2Name = app.getUserInput("Enter Player Two Name")
    player2 = Player("sug")

    return Game(player1, player2)

def keyPressed(app, event):
    app.UI = loadGameUI(app)
    if event.key == "Down":
        app.curRow -= app.scale/100
        if app.curRow < 0:
            app.curRow = 0
    if event.key == "Up":
        app.curRow += app.scale/100
        if app.curRow > len(app.curBoard) - 1:
            app.curRow = len(app.curBoard) - 1
    if event.key == "Right":
        app.curCol -= app.scale/100
        if app.curCol < 0:
            app.curCol = 0
    if event.key == "Left":
        app.curCol += app.scale/100
        if app.curCol > len(app.curBoard[0]) - 1:
            app.curCol = len(app.curBoard[0]) - 1
    if event.key == "p":
        app.scale += 10
        if app.scale > 200:
            app.scale = 200
    if event.key == "o":
        app.scale -= 10
        if app.scale < 10:
            app.scale = 10

def purcahseBuildingsList(app, row, col):
    app.UI.append(Button(20, 60, 100, 100, "GoldMine",
        lambda: app.game.curAlly.purchase((row,col), GoldMine())))
    app.UI.append(Button(20, 120, 100, 160, "Barracks",
        lambda: app.game.curAlly.purchase((row,col), Barracks())))
    app.UI.append(Button(20, 180, 100, 220, "Factory",
        lambda: app.game.curAlly.purchase((row,col), Factory())))

def mousePressed(app, event):
    for button in app.UI:
        if button.checkClicked(event.x, event.y):
            app.UI = loadGameUI(app)
            button.onClick()
            update(app)
            return

    boardCol = round((event.x - (app.curCol * app.scale)) / app.scale)
    boardRow = round((event.y - (app.curRow * app.scale)) / app.scale)
    if (boardCol >= 0 and boardCol < len(app.curBoard[0]) and
        boardRow >= 0 and boardRow < len(app.curBoard)):
        app.UI = loadGameUI(app)
        if app.game.curAlly.isContructionZone(boardRow, boardCol):
            x0 = ((boardCol + app.curCol) * app.scale) - app.scale/2
            y0 = ((boardRow + app.curRow) * app.scale) - app.scale/2
            app.UI.append(Button(x0, y0, x0 + app.scale, y0 + app.scale, "Buy?",
                lambda: purcahseBuildingsList(app, boardRow, boardCol)))
            return

def mouseDragged(app, event):
    pass

def update(app):
    app.curBoard = app.game.curAlly.buildings

def drawRoom(app, canvas, row, col, room):
    smallSide = min(app.width, app.height)
    unit = smallSide/app.scale
    if room == None:
        roomImage = app.images["Empty"]
    else:
        roomImage = app.images[room.name]
    imageWidth, imageHeight = roomImage.size
    roomImage = app.scaleImage(roomImage, app.scale/imageWidth)
    x = (col + app.curCol) * app.scale
    y = (row + app.curRow) * app.scale
    canvas.create_image(x, y, image=ImageTk.PhotoImage(roomImage))

def drawMap(app, canvas):
    for row in range(len(app.curBoard)):
        for col in range(len(app.curBoard[0])):
            drawRoom(app, canvas, row, col, app.curBoard[row][col])
        
def drawUI(app, canvas):
    for button in app.UI:
        canvas.create_rectangle(button.x0, button.y0, button.x1, button.y1,
        fill = "gray", outline = "black",width = 5)
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