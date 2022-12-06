
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