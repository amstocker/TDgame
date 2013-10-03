from core.classes import *




class TD(Core):
    def __init__(self):
        Core.__init__(self)
        self.menu = Menu(self.font2)       

        # tower data
        self.particles = []
        self.towers = []

        # creep data
        self.show_waypoints = True
        self.creeps = []
        self.creep_path = Dijkstra(self.grid, (0,0), (10,10))
        self.nocreeps = True
        self.creep_spawn_clock = pygame.time.Clock()
        self.spawn_threshold = 0
        self.spawn_frequency = 500

        # score (won't work yet?)
        self.score = 0
    
    def mouseDown(self, button, pos):
        if button == 3:
            if self.creeps != []:
                self.creeps[0].waypoints = Dijkstra(self.grid, self.grid.getNode(self.creeps[0].pos), self.grid.getNode(pos))
    
    def mouseUp(self, button, pos):
        if button == 1:
            if self.menu.getClick(pos) == False:
                node = self.grid.getNode(pos)
                # can't build on space station
                if node[1] > 15 and node[0] > 15:
                    pass
                elif self.grid.Grid[node] == 0:
                    self.grid.insert(node, 1)
                    if self.menu.selected == self.menu.item4:
                        l = LaserTower(self.grid, pos)
                        self.towers.append(l)
                    elif self.menu.selected == self.menu.item3:
                        f = FireTower(self.grid, pos)
                        self.towers.append(f)
                    else:
                        d = DefaultTower(self.grid, pos)
                        self.towers.append(d)
                    # splice path?
                    for c in self.creeps:
                        c.waypoints = Dijkstra(self.grid, self.grid.getNode(c.pos), (17,17))
                
    def mouseMotion(self, buttons, pos, rel):
        self.menu.getHover(pos)

    def update(self):
        # update creep spawn
        self.creep_spawn_clock.tick()
        self.spawn_threshold += self.creep_spawn_clock.get_time()
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
        # update menu
        self.menu.update()
        if self.menu.scrolling == True:
            self.menu.scroll()
        # update towers and particles
        if self.nocreeps == False:
            for c in self.creeps:
                c.update(self.grid, self.creeps, self.particles, self.score)
        for t in self.towers:
            t.update(self.particles, self.creeps)
        for p in self.particles:
            p.update(self.particles, self.creeps)

    def keyUp(self, key):
        if key == K_w:
            self.show_waypoints = not self.show_waypoints

    def draw(self):
        self.screen.blit(self.background, (0,0))
        for t in self.towers:
            t.render(self.screen)
        for c in self.creeps:
            c.render(self.screen, self.grid, self.show_waypoints)
        for p in self.particles:
            p.render(self.screen)
        self.menu.render(self.screen)

TD = TD()
TD.mainLoop(40)
