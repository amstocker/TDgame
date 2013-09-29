from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform, randint
from ai import *

# convert vec2d elements into integers (copyright Bill Cauchois 2013)
def intvec(v):
    return vec2d(int(v[0]), int(v[1]))




class Agent:
    def __init__(self, r, vmax):
        self.r = r
        self.vmax = vmax

        self.pos = vec2d(0,0)
        self.waypoints = []
            
    def update(self, grid):
        dir = grid.getCoordinate(self.waypoints[0]) - self.pos
        if dir.length > self.r:
            dir.length = self.vmax
            self.pos += dir
        elif len(self.waypoints) > 1:
            self.waypoints.pop(0)
        elif 3 < dir.length <= self.r:
            dir.length = self.vmax
            self.pos += dir

    def render(self, screen, grid):
        for i in xrange(len(self.waypoints)):
            pygame.draw.circle(screen, (255,50,0), grid.getCoordinate(self.waypoints[i]), 5, 1)
            if i+1 < len(self.waypoints):
                pygame.draw.line(screen, (255,50,0), grid.getCoordinate(self.waypoints[i]), \
                                 grid.getCoordinate(self.waypoints[i+1]), 1)
        pygame.draw.circle(screen, (0,0,0), intvec(self.pos), int(self.r)+1)
        pygame.draw.circle(screen, (0,100,255), intvec(self.pos), int(self.r))



class Grid:
    # n across, m down
    def __init__(self, n, m, resolution):
        self.n = n
        self.m = m
        self.Grid = [[0]*m]*n
        self.dx = resolution[0]/n
        self.dy = resolution[1]/m

    def getNode(self, v):
        v= intvec(v)
        return ((v[0]+1)/self.dx, (v[1]+1)/self.dy)

    def getCoordinate(self, p):
        return vec2d(1+self.dx/2+self.dx*p[0], 1+self.dy/2+self.dy*p[1])

    def render(self, screen):
        for i in xrange(self.n):
            for j in xrange(self.m):
                if self.Grid[i][j] == 1:
                    c = self.getCoordinate((i, j))
                    rect = [c[0]-self.dx/2, c[1]-self.dy/2, self.dx, self.dy]
                    pygame.draw.rect(screen, (0,0,0), rect)



class Core(PygameHelper):
    def __init__(self):
        # set pygame vars
        self.w, self.h = 481, 436
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        self.background = pygame.image.load('grid.jpeg').convert()
        # grid
        self.grid = Grid(32, 29, (481,436))

        # initialize agent with random target
        self.A = Agent(7, 5)
        v = (randint(0,32), randint(0,29))
        self.A.waypoints = Dijkstra(self.grid, self.grid.getNode(self.A.pos), v)

    def keyDown(self, key):
        pass
                
    def keyUp(self, key):
        pass

    def mouseDown(self, button, pos):
        if button == 3:
            self.A.waypoints = Dijkstra(self.grid, self.grid.getNode(self.A.pos), self.grid.getNode(pos))
    
    def mouseUp(self, button, pos):
        if button == 1:
            n = self.grid.getNode(pos)
            print self.grid.Grid[n[0]]
            print n[0], n[1]
            self.grid.Grid[n[0]][n[1]] = 1
            print self.grid.Grid
        
    def mouseMotion(self, buttons, pos, rel):
        pass
    
    def update(self):
        self.A.update(self.grid)
        
    def draw(self):
        self.screen.blit(self.background, (0,0))
        self.grid.render(self.screen)
        self.A.render(self.screen, self.grid)
        

c = Core()
c.mainLoop(40)
