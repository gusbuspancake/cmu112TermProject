# Demolition Dungeons
# made by Gus Gurley

from cmu_112_graphics import *

from Game import Game
from Player import Player
from Buildings import GoldMine, Barracks, Factory, Entrance
from Traps import Bomb
from Troops import Soldier

import math

# https://docs.python.org/3/library/pickle.html
import pickle

# https://www.geeksforgeeks.org/python-list-files-in-a-directory/
import os

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

    def __repr__(self):
        return f'{self.text}'

def appStarted(app):
    # scale is the n by n pixel dimmensions of one room
    app.scale = 100

    app.cameraY = 50
    app.cameraX = 0
    app.font = "Century 14 bold"
    app.UI = loadMenuUI(app)

    app.menu = True

def makeGame(app, game):
    app.menu = False
    app.game = game
    app.sameSide = True
    app.troopMove = None
    app.needsTarget = None

    app.UI = loadGameUI(app)
    app.images = loadImages(app)
    app.curBoard = app.game.curAlly.buildings

def makeNewGame(app):
    player1Name = app.getUserInput("Enter Player One Name")
    player1 = Player(player1Name)
    player2Name = app.getUserInput("Enter Player Two Name")
    player2 = Player(player2Name)

    makeGame(app, Game(player1, player2))

def getSaves():
    path = "saves/"
    files = os.listdir(path)
    files = filter(lambda x: not x.startswith("."), files)
    return files

def saveGame(app):
    fileName = app.getUserInput("Enter Save Name")
    if fileName == None:
        return
    file = open("saves/" + fileName, "wb")
    pickle.dump(app.game, file)
    file.close()

def loadGame(fileName, app):
    file = open("saves/" + fileName, "rb")
    game = pickle.load(file)
    file.close()
    makeGame(app, game)    

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
    result["Ruin"] = app.loadImage("assets/ruins.jpeg")
    #https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.freepik.com%2Ffree-v
    #ector%2Fcartoon-stone-texture_976364.htm&psig=AOvVaw3Ji3e0i1GfeGA942D9mamQ
    #&ust=1670172451598000&source=images&cd=vfe&ved=0CA8QjRxqFwoTCJif5a_z3fsCFQ
    #AAAAAdAAAAABAD
    result["Rock"] = app.loadImage("assets/rock.jpg")
    return result

def loadMenuUI(app):
    result = []
    result.append(Button(app.width/2 - 100, app.height/2 - 30,
        app.width/2 + 100, app.height/2 + 30,
        "Start New Game!", lambda: makeNewGame(app)))
    result.append(Button(app.width/2 - 100, app.height/2 + 60,
        app.width/2 + 100, app.height/2 + 120,
        "Load Game!", lambda: savesUI(app)))
    return result

def savesUI(app):
    app.UI = []
    i = 0
    j = 0
    for save in getSaves():
        i += 1
        if i == 4:
            i = 1
            j += 1
        app.UI.append(Button((150*i), 400+(100*j), 100+(150*i), 450+(100*j),
            save, lambda: loadGame(save, app)))

def loadGameUI(app):
    result = []
    result.append(Button(10, app.height - 50, 90, app.height - 10,
                    "End Turn", app.game.endTurn))
    result.append(Button(app.width - 120, app.height - 110, app.width - 10,
                    app.height - 70, "Help", lambda: loadInfoUI(app)))
    if app.sameSide:
        result.append(Button(app.width - 120, app.height - 50, app.width - 10,
                    app.height - 10, "Go To Enemy", lambda: switchSides(app)))
    else:
        result.append(Button(app.width - 120, app.height - 50, app.width - 10,
                    app.height - 10, "Return Home", lambda: switchSides(app)))
    return result

def loadInfoUI(app):
    app.UI.append(Button((app.width/2) - 75, (app.height/2) - 50,
                (app.width/2) + 75, (app.height/2) + 50, 
                "  Open Read Me\nFor Instructions!"))

def loadGameOverUI(app):
    result = []
    result.append(Button(app.width/2 - 100, app.height/2 - 30,
        app.width/2 + 100, app.height/2 + 30,
        "Play Again?", lambda: runApp(width = 800, height = 800)))
    return result

def switchSides(app):
    app.sameSide = not app.sameSide
    app.UI = loadGameUI(app)
    update(app)

def keyPressed(app, event):
    if app.menu:
        app.UI = loadMenuUI(app)
    elif app.game.loser == None:
        app.UI = loadGameUI(app)

        if event.key == "i" or event.key == "I":
            loadInfoUI(app)
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
        if event.key == "Escape":
            app.UI.append(Button((app.width/2) - 50, (app.height/2) - 25,
                (app.width/2) + 50, (app.height/2) + 25, "Save?",
                lambda: saveGame(app)))
        
        app.scale = min(app.scale, 300)
        maxScale = max(app.width/len(app.curBoard[0]),
            app.height/len(app.curBoard))
        app.scale = max(app.scale, maxScale)
        app.scale = round(app.scale)
        app.cameraX = min(app.cameraX, 0)
        app.cameraY = min(app.cameraY, 50)
        app.cameraX = max(app.cameraX, app.width-len(app.curBoard[0])*app.scale)
        app.cameraY = max(app.cameraY, app.height - len(app.curBoard)*app.scale)
    else:
        app.ui = loadGameOverUI(app)
    
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
    health = f"Room HP: {room.health}\n"
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
    info = health + allyTroops + enemyTroops + traps

    app.UI.append(Button(app.width-310, 60, app.width-10, 360, info))

def showTheirInsides(app, room):
    health = f"Room HP: {room.health}\n"
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
    info = health + allyTroops + enemyTroops

    app.UI.append(Button(app.width-310, 60, app.width-10, 360, info))

def mousePressed(app, event):
    
    if app.menu:
        for button in app.UI:
            if button.checkClicked(event.x, event.y):
                button.onClick()
                return
        app.UI = loadMenuUI(app)
    elif not app.game.loser == None:
        app.UI = loadGameOverUI(app)
        for button in app.UI:
            if button.checkClicked(event.x, event.y):
                button.onClick()
                return
    else:
        for button in app.UI:
            if button.checkClicked(event.x, event.y):
                app.UI = loadGameUI(app)
                button.onClick()
                update(app)
                if not app.game.loser == None:
                    app.UI = loadGameOverUI(app)
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
                app.UI.append(Button(x0, y0, x0 + app.scale,
                    y0 + app.scale, "Buy?",
                    lambda: purcahseBuildingsList(app, boardRow, boardCol)))
                return
            room = app.curBoard[boardRow][boardCol]
            if not app.needsTarget == None:
                app.needsTarget((boardRow, boardCol))
                app.needsTarget = None

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
    rock = app.images["Rock"]
    imageWidth, imageHeight = rock.size
    rock = app.scaleImage(rock, app.scale/imageWidth)
    
    x = (col * app.scale) + app.cameraX
    y = (row * app.scale) + app.cameraY

    canvas.create_image(x + (app.scale / 2), y + (app.scale / 2),
        image=ImageTk.PhotoImage(rock))
    
    if not room == None:
        roomImage = app.images[room.name]
        imageWidth, imageHeight = roomImage.size
        roomImage = app.scaleImage(roomImage, app.scale/imageWidth)
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

def drawMenu(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "gray")
    canvas.create_text(app.width/2, app.height/4,
        text = "WELCOME TO", font = "Century 64 bold")
    canvas.create_text(app.width/2, (app.height/4) + 100,
        text = "DEMOLITION DUNGEONS", font = "Century 64 bold")

def drawGameOver(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "black")
    canvas.create_text(app.width/2, app.height/4,
        text = "GAME OVER", font = "Century 64 bold", fill = "Red")
    canvas.create_text(app.width/2, (app.height/4) + 100,
        text = f"{app.game.loser.name} LOST!", font = "Century 64 bold",
        fill = "Red")

def redrawAll(app, canvas):
    if app.menu:
        drawMenu(app, canvas)
    elif app.game.loser == None:
        drawMap(app, canvas)
        drawResources(app, canvas)
    else:
        drawGameOver(app, canvas)

    drawUI(app, canvas)

runApp(width = 800, height = 800)