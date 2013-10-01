from core.classes import *




class TD(Core):
    def __init__(self):
        Core.__init__(self)
        self.menu = Menu(self.font2)       

        self.particles = []
        self.towers = []
        self.creeps = []
        self.creep_path = Dijkstra(self.grid, (0,0), (10,10))
        self.nocreeps = True
    
    def mouseDown(self, button, pos):
        if button == 3:
            if self.creeps != []:
                self.creeps[0].waypoints = Dijkstra(self.grid, self.grid.getNode(self.creeps[0].pos), self.grid.getNode(pos))
    
    def mouseUp(self, button, pos):
        if button == 1:
            if self.menu.getClick(pos) == False:
                node = self.grid.getNode(pos)
                if self.grid.Grid[node] == 0:
                    self.grid.insert(node, 1)
                    t = Tower(self.grid, pos, len(self.towers), 1000)
                    self.towers.append(t)
                    for c in self.creeps:
                        c.waypoints = Dijkstra(self.grid, self.grid.getNode(c.pos), (10,10))
                
        
    def mouseMotion(self, buttons, pos, rel):
        self.menu.getHover(pos)
##        if buttons[0] == 1 and len(self.creeps) > 0:
##            node = self.grid.getNode(pos)
##            if self.grid.Grid[node] == 0:
##                self.grid.insert(node, 1)
##                t = Tower(self.grid, pos, len(self.towers), 1000)
##                t.target = self.creeps[0]
##                self.towers.append(t)
            

    def update(self):
        if self.menu.scrolling == True:
            self.menu.scroll()
        if self.nocreeps == True:
            self.nocreeps = False
            C = Creep((randint(0,255), randint(0,255), randint(0,255)), 10, 6, 50)
            C.waypoints = Dijkstra(self.grid, (0,0), (10,10))
            self.creeps.append(C)
        if len(self.creeps) == 0 and self.nocreeps == False:
            self.nocreeps = True
        if self.nocreeps == False:
            for t in self.towers:
                t.target = self.creeps[0]
            for c in self.creeps:
                c.update(self.grid, self.creeps, self.particles)
        for t in self.towers:
            t.update(self.particles, self.creeps)
        for p in self.particles:
            p.update(self.particles, self.creeps)

    def draw(self):
        self.screen.blit(self.background, (0,0))
        for c in self.creeps:
            c.render(self.screen, self.grid)
        for t in self.towers:
            t.render(self.screen, self.grid)
        for p in self.particles:
            p.render(self.screen)
        self.menu.render(self.screen)

TD = TD()
TD.mainLoop(40)
