from core.classes import *


class TD(Core):
    def __init__(self):
        Core.__init__(self)
        self.menu = Menu(self.font2)       

        self.particles = []
        self.towers = []
        self.slowtowers = []

        self.show_waypoints = True
        self.creeps = []
        self.creep_path = Dijkstra(self.grid, (0,0), (10,10))
        self.creep_spawn_clock = pygame.time.Clock()
        self.spawn_threshold = 0
        self.spawn_frequency = 200

        # score (won't work yet?)
        self.score = 0
    
    def mouseDown(self, button, pos):
        pass
    
    def mouseUp(self, button, pos):
        if button == 1:
            if self.menu.getClick(pos) == False:
                node = self.grid.getNode(pos)
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
                    elif self.menu.selected == self.menu.item2:
                        s = SlowTower(self.grid, pos)
                        self.slowtowers.append(s)
                    else:
                        d = DefaultTower(self.grid, pos)
                        self.towers.append(d)
                    for c in self.creeps:
                        if node in c.waypoints:
                            c.waypoints = Dijkstra(self.grid, self.grid.getNode(c.pos), (17,17))
                
    def mouseMotion(self, buttons, pos, rel):
        self.menu.getHover(pos)

    def update(self):
        self.creep_spawn_clock.tick()
        self.spawn_threshold += self.creep_spawn_clock.get_time()
        if self.spawn_threshold > self.spawn_frequency:
            self.spawn_threshold = 0
            self.spawnRandomCreep()
        self.menu.update()
        if self.menu.scrolling == True:
            self.menu.scroll()
        if len(self.creeps) > 0:
            for c in self.creeps:
                c.update(self.grid, self.creeps, self.particles, self.score)
        for t in self.towers:
            t.update(self.particles, self.creeps)
        for s in self.slowtowers:
            s.update(self.particles, self.creeps)
        for p in self.particles:
            p.update(self.particles, self.creeps)

    def keyUp(self, key):
        if key == K_w:
            self.show_waypoints = not self.show_waypoints

    def draw(self):
        self.screen.blit(self.background, (0,0))
        for t in self.towers:
            t.render(self.screen)
        for s in self.slowtowers:
            s.render(self.screen)
        for c in self.creeps:
            c.render(self.screen, self.grid, self.show_waypoints)
        for p in self.particles:
            p.render(self.screen)
        self.menu.render(self.screen)

TD = TD()
TD.mainLoop(40)
