from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform, randint

# convert vec2d elements into integers (copyright Bill Cauchois 2013)
def intvec(v):
    return vec2d(int(v[0]), int(v[1]))




class Agent:
    def __init__(self, color, r, vmax, hp):
        self.color = color
        self.r = r
        self.vmax = vmax
        self.hp = hp
        self.pos = vec2d(0,0)
        self.waypoints = []
            
    def update(self, grid):
        if self.hp < 0:
            # do something
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
            pygame.draw.circle(screen, (0,0,0), grid.getCoordinate(self.waypoints[i]), 5, 1)
            if i+1 < len(self.waypoints):
                pygame.draw.line(screen, (0,0,0), grid.getCoordinate(self.waypoints[i]), \
                                 grid.getCoordinate(self.waypoints[i+1]), 1)
        pygame.draw.circle(screen, (0,0,0), intvec(self.pos), int(self.r)+1)
        pygame.draw.circle(screen, self.color, intvec(self.pos), int(self.r))




class Projectile:
    # target is Agent class
    def __init__(self, pos, target):
        self.pos = vec2d(pos)
        self.vel = 0
        self.dir = vec2d(0,0)
        self.color = (255,255,255)
        self.target = target
        
    def update(self, particles_list):
        self.dir = self.target.pos - self.pos
        if self.dir.length < self.target.r:
            self.target.hp -= 1
            particles_list.remove(self)
        self.dir.length = self.vel
        self.pos += self.dir
        
    def render(self, screen):
        pygame.draw.line(screen, self.color, self.pos, self.pos+self.dir, 2)
        


class Tower:
    def __init__(self, grid, pos, timer_id, freq):
        self.node = grid.getNode(pos)
        self.pos = grid.getCoordinate(self.node)
        self.freq = freq
        pygame.time.set_timer(24, self.freq)
        self.target = 0
        self.color = (59,255,121)
        
    def update(self, particles_list):
        if self.target != 0:
            p = Projectile(self.pos, self.target)
            p.vel = 10
            p.color = self.color
            particles_list.append(p)
            pygame.time.set_timer(24, self.freq)
            
    def render(self, screen, grid):
        c = self.pos
        rect = [c[0]-grid.dx/2, c[1]-grid.dy/2, grid.dx-1, grid.dy-1]
        pygame.draw.rect(screen, self.color, rect)
    




class Grid:
    # n across, m down
    def __init__(self, n, m, resolution):
        self.n = n
        self.m = m
        self.Grid = {}
        for i in xrange(n):
            for j in xrange(m):
                self.Grid[(i,j)] = 0
        self.dx = resolution[0]/n
        self.dy = resolution[1]/m

    def getNode(self, v):
        v = intvec(v)
        return ((v[0]+1)/self.dx, (v[1]+1)/self.dy)

    def getCoordinate(self, p):
        return vec2d(self.dx/2+self.dx*p[0], self.dy/2+self.dy*p[1])

##    def render(self, screen):
##        for i in xrange(self.n):
##            for j in xrange(self.m):
##                if self.Grid[(i, j)] == 1:
##                    c = self.getCoordinate((i, j))
##                    rect = [c[0]-self.dx/2, c[1]-self.dy/2, self.dx, self.dy]
##                    pygame.draw.rect(screen, (0,0,0), rect)

    def insert(self, node, value):
        self.Grid[node] = value




# minimum distance priority queue
class BinaryHeap:
    def __init__(self):
        self.heap = [0,[0,-1],[0,-1],[0,-1]]
        self.size = 0

    # node in [(x, y), cost] form
    def insert(self, node):
        if self.size == len(self.heap)-1:
            self.heap += [[0,-1]]*(self.size+1)
        self.size += 1
        pos = self.size
        while pos > 1 and node[1] < self.heap[pos/2][1]:
            self.heap[pos] = self.heap[pos/2]
            pos /= 2
        self.heap[pos] = node

    def remove_priority(self):
        if self.size == 1:
            priority = self.heap[1]
            self.heap[1] = [0,-1]
            self.size = 0
            return priority
        elif self.size > 0:
            priority = self.heap[1]
            node = self.heap[self.size]
            self.heap[self.size] = [0,-1]
            self.size -= 1
            pos = 1
            while pos <= self.size/2:
                lchild = self.heap[2*pos]
                rchild = self.heap[2*pos+1]
                if node[1] > max(lchild[1],rchild[1]) > -1:
                    if lchild[1] <= rchild[1] or rchild[1] == -1:
                        self.heap[pos] = lchild
                        pos = 2*pos
                    else:
                        self.heap[pos] = rchild
                        pos = 2*pos+1
                elif node[1] > min(lchild[1],rchild[1]) > -1:
                    if lchild[1] < rchild[1]:
                        self.heap[pos] = lchild
                        pos = 2*pos
                    else:
                        self.heap[pos] = rchild
                        pos = 2*pos+1
                else:
                    break
            self.heap[pos] = node
            return priority
        else:
            return -1




# source and target in (x,y) form
def Dijkstra(grid, source, target):
    # distances and parents dictionary
    D = {}
    # visited vertices stack
    S = []
    # priority queue for minimum distance node
    Q = BinaryHeap()

    maxn = grid.n
    maxm = grid.m
    # dictionary initiation
    for n in xrange(grid.n):
        for m in xrange(grid.m):
            if (n, m) == source:
                D[(n, m)] = (0, source)
            else:
                # since there are less than 1000 nodes on the graph, 1000 can serve as /infinite/ distance
                D[(n, m)] = (1000, 0)
    Q.insert([source, 0])
    # main loop
    while Q.size > 0:
        x = Q.remove_priority()
        if x[0] == target:
            break
        if x[1] == 1000:
            break
        S.insert(0, x[0])
        # for each v near x
        for i in [[1,0], [0,1], [-1,0], [0,-1]]:
            # maxn, maxm are size of grid
            if maxn > x[0][0]+i[0] >= 0 and maxm > x[0][1]+i[1] >= 0:
                v = (x[0][0]+i[0], x[0][1]+i[1])
                if v not in S:
                    # where 1 is the dist between adjacent nodes, 1000 if wall (diagonals excluded)
                    if grid.Grid[v] == 1:
                        dist = 1000
                    else:
                        dist = 1
                    d = D[x[0]][0] + dist
                    if d < D[v][0]:
                        D[v] = (d, x[0])
                        Q.insert([v, d])
    # retrieve path
    waypoints = [target]
    p = target
    while p != source:
        if p == 0:
            return [source]
        p = D[p][1]
        waypoints.insert(0, p)
    return waypoints



### --- CORE EVENT FUNCTIONS ---
class Core(PygameHelper):
    def __init__(self):
        # set pygame vars
        self.w, self.h = 659, 659
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        self.background = pygame.image.load('img/abstract.jpg').convert()
        # init grid
        self.grid = Grid(20, 20, (self.w+1,self.h+1))

    def keyDown(self, key):
        pass
                
    def keyUp(self, key):
        pass

    def mouseDown(self, button, pos):
        pass
    
    def mouseUp(self, button, pos):
        pass
        
    def mouseMotion(self, buttons, pos, rel):
        pass
    
    def update(self):
        pass
        
    def draw(self):
        pass

