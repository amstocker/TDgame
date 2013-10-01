from core.classes import *




class TD(Core):
    def __init__(self):
        Core.__init__(self)
        self.menu = Menu(self.font2)       

        # tower data
        self.particles = []
        self.towers = []

        # creep data
        self.creeps = []
        self.creep_path = Dijkstra(self.grid, (0,0), (10,10))
        self.nocreeps = True
        self.creep_spawn_clock = pygame.time.Clock()
        self.spawn_threshold = 0
        self.spawn_frequency = 2000

        # score
        self.score = 0
    
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
                    t = Tower(self.grid, pos, 1000)
                    self.towers.append(t)
                    for c in self.creeps:
                        c.waypoints = Dijkstra(self.grid, self.grid.getNode(c.pos), (10,10))
                
        
    def mouseMotion(self, buttons, pos, rel):
        self.menu.getHover(pos)
##        if buttons[0] == 1 and len(self.creeps) > 0:
##            node = self.grid.getNode(pos)
##            if self.grid.Grid[node] == 0:
##                self.grid.insert(node, 1)
##                t = Tower(self.grid, pos, 1000)
##                t.target = self.creeps[0]
##                self.towers.append(t)
            

    def update(self):
        self.spawn_frequency = 2000-self.score
        self.creep_spawn_clock.tick()
        self.spawn_threshold += self.creep_spawn_clock.get_time()
        if self.menu.scrolling == True:
            self.menu.scroll()
        if self.nocreeps == True:
            self.nocreeps = False
            # need to figure out a way when spawning multiple creeps, or when building,
            # for how to easily keep a variable pathway but keep creeps on it at all times.
            # i'm thinking that it would be possible to find the node clicked on for building,
            # and just find the best pathing from eitherside of it and then slice everything together.
            self.spawnRandomCreep()
        elif self.spawn_threshold > self.spawn_frequency:
            self.spawn_threshold = 0
            self.spawnRandomCreep()
        if len(self.creeps) == 0:
            self.nocreeps = True
        if self.nocreeps == False:
            for t in self.towers:
                t.target = self.creeps[0]
            for c in self.creeps:
                c.update(self.grid, self.creeps, self.particles, self.score)
        for t in self.towers:
            t.update(self.particles, self.creeps)
        for p in self.particles:
            p.update(self.particles, self.creeps)

    def draw(self):
        self.screen.blit(self.background, (0,0))
        for t in self.towers:
            t.render(self.screen)
        for c in self.creeps:
            c.render(self.screen, self.grid)
        for p in self.particles:
            p.render(self.screen)
        self.menu.render(self.screen)

TD = TD()
TD.mainLoop(40)
