from core.classes import *




class TD(Core):
    def __init__(self):
        Core.__init__(self)
        # initialize agent with random target
        first = Creep((0,0,0), 10, 6, 100)
        v = (randint(0,10), randint(0,10))
        first.waypoints = Dijkstra(self.grid, self.grid.getNode(first.pos), v)
        
        self.particles = []
        self.towers = []
        self.creeps = [first]

        self.nocreeps = False
    
    def userEvent(self):
        for t in self.towers:
            t.update(self.particles, self.creeps)
    
    def mouseDown(self, button, pos):
        if button == 3:
            if self.creeps != []:
                self.creeps[0].waypoints = Dijkstra(self.grid, self.grid.getNode(self.creeps[0].pos), self.grid.getNode(pos))
    
    def mouseUp(self, button, pos):
        if button == 1:
            t = Tower(self.grid, pos, 24+len(self.towers), 1000)
            self.towers.append(t)
            node = self.grid.getNode(pos)
            self.grid.insert(node, 1)
        
    def mouseMotion(self, buttons, pos, rel):
        if buttons[0] == 1 and len(self.creeps) > 0:
            t = Tower(self.grid, pos, 24+len(self.towers), 1000)
            t.target = self.creeps[0]
            self.towers.append(t)
            node = self.grid.getNode(pos)
            self.grid.insert(node, 1)

    def update(self):
        if self.nocreeps == True:
            self.nocreeps = False
            C = Creep((0,0,0), 10, 6, 100)
            v = (randint(0,10), randint(0,10))
            C.waypoints = Dijkstra(self.grid, self.grid.getNode(C.pos), v)
            self.creeps.append(C)
        if len(self.creeps) == 0 and self.nocreeps == False:
            self.nocreeps = True
        if self.nocreeps == False:
            for t in self.towers:
                t.target = self.creeps[0]
            for c in self.creeps:
                c.update(self.grid, self.creeps, self.particles)
        for p in self.particles:
            p.update(self.particles, self.creeps)

    def draw(self):
        self.screen.blit(self.background, (0,0))
        for c in self.creeps:
            c.render(self.screen, self.grid)
        for t in self.towers:
            t.render(self.screen, self.grid, self.rendered_numbers)
        for p in self.particles:
            p.render(self.screen)

TD = TD()
TD.mainLoop(40)
