

class Trap():
    def __init__(self):
        pass

    def __repr__(self):
        return f'{self.name}'

class Bomb(Trap):
    def __init__(self):
        self.cost = ("Gold", 10)
        self.name = "Bomb"
    
    # deals 25 damage to all enemy troops in the room
    def trip(self, buildings, roomCords, room, regiment):
        for troop in regiment.troops:
            troop.curHealth -= 25
        regiment.cleanOutDead(room)
        room.traps.remove(self)

class Snare(Trap):
    def __init__(self):
        self.cost = ("Gold", 20)
        self.name = "Snare"
    
    # sets current movement of enemies in room to 0
    def trip(self, buildings, roomCords, room, regiment):
        for troop in regiment.troops:
            troop.curMovement = 0
        room.traps.remove(self)
