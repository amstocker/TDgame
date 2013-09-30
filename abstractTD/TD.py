from core.classes import *


class TD(Core):
    def __init__(self):
        Core.__init__(self)
        # initialize agent with random target
        self.A = Agent((0,0,0), 10, 6, 100)
        v = (randint(0,10), randint(0,10))
        self.A.waypoints = Dijkstra(self.grid, self.grid.getNode(self.A.pos), v)

        self.particles = []
        self.towers = []
    
    def userEvent(self):
        for t in self.towers:
            t.update(self.particles)
    
    def mouseDown(self, button, pos):
        if button == 3:
            self.A.waypoints = Dijkstra(self.grid, self.grid.getNode(self.A.pos), self.grid.getNode(pos))
    
    def mouseUp(self, button, pos):
        if button == 1:
            t = Tower(self.grid, pos, 24+len(self.towers), 1000)
            t.target = self.A
            self.towers.append(t)
            node = self.grid.getNode(pos)
            self.grid.insert(node, 1)

        
    def mouseMotion(self, buttons, pos, rel):
        if buttons[0] == 1:
            t = Tower(self.grid, pos, 24+len(self.towers), 1000)
            t.target = self.A
            self.towers.append(t)
            node = self.grid.getNode(pos)
            self.grid.insert(node, 1)

    def update(self):
        self.A.update(self.grid)
        for p in self.particles:
            p.update(self.particles)

    def draw(self):
        self.screen.blit(self.background, (0,0))
        # self.grid.render(self.screen)
        self.A.render(self.screen, self.grid)
        for t in self.towers:
            t.render(self.screen, self.grid)
        for p in self.particles:
            p.render(self.screen)

TD = TD()
TD.mainLoop(40)
