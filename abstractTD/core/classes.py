from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform, randint

# convert vec2d elements into integers (copyright Bill Cauchois 2013)
def intvec(v):
    return vec2d(int(v[0]), int(v[1]))

# colors
# frost tower: 102 254 236
# fire tower: 235 52 82
# laser tower: 91 52 235


# --- MENU CLASSES ---

class Menu:
    def __init__(self, font, show=True):
        self.show = show
        self.font = font
        self.menutext = self.font.render("build", False, (0,0,0))

        # menu scrolling
        self.scrolling = False
        self.scroll_pos = 0
        self.extended = False
        self.h = 627
        
    def getClick(self, pos):
        if self.extended == False and 132 >= pos[0] >= 0 and 659 >= pos[1] >= self.h-2: #625:
            self.scrolling = True
            return True
        elif self.extended == True and 132 >= pos[0] >= 0 and 659 >= pos[1] >= self.h-2: #527:
            self.scrolling = True
            return True
        else:
            return False
        
    def getHover(self, pos):
        pass
    
    def scroll(self):
        if self.extended == False:
            if self.scroll_pos < 99:
                self.scroll_pos += 11
            else:
                self.scrolling = False
                self.extended = True
        else:
            if self.scroll_pos > 0:
                self.scroll_pos -= 11
            else:
                self.scrolling = False
                self.extended = False
        self.h = 627-self.scroll_pos
        
    def render(self, screen):
        rect = [1, self.h, 130, 131]
        rect_outline = [0, self.h-1, 131, 132]
        pygame.draw.rect(screen, (0,0,0), rect_outline)
        pygame.draw.rect(screen, (255,255,255), rect)
        rect_overlap = [1, 627, 130, 31]
        pygame.draw.rect(screen, (255,255,255), rect_overlap)
        screen.blit(self.menutext, (5, 629))
        


# --- CREEP CLASSES ---

class Creep:
    def __init__(self, color, r, vmax, hp):
        self.color = color
        self.r = r
        self.vmax = vmax
        self.maxhp = hp
        self.hp = hp
        self.pos = vec2d(0,0)
        self.waypoints = []
        self.slowed = False
            
    def update(self, grid, creeps, particles_list):
        if self.hp <= 0:
            creeps.remove(self)
            for p in xrange(20):
                rdir = vec2d(uniform(-5,5), uniform(-5,5))
                p = Particle()
                p.color = self.color
                p.pos = (self.pos[0]+randint(-1,1),self.pos[1]+randint(-1,1))
                p.vel = rdir
                particles_list.append(p)
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
        pygame.draw.line(screen, (0,0,0), (self.pos[0]-self.r, self.pos[1]-self.r-5), \
                         (self.pos[0]+self.r, self.pos[1]-self.r-5), 5)
        hplossratio = 1-float(self.hp)/self.maxhp
        pygame.draw.line(screen, (146,252,116), (self.pos[0]-self.r+1, self.pos[1]-self.r-5), \
                         (self.pos[0]+self.r-(hplossratio*1.8*self.r)-1, self.pos[1]-self.r-5), 3)




# --- TOWER CLASSES ---

class Tower:
    def __init__(self, grid, pos, timer_id, freq):
        self.node = grid.getNode(pos)
        self.pos = grid.getCoordinate(self.node)
        
        # timing
        self.freq = freq
        self.clock = pygame.time.Clock()
        self.threshold = 0
        
        self.target = 0
        self.color = (101,255,102)
        self.upgrade = 3
        self.range = 200
        
    def update(self, particles_list, creeps):
        self.clock.tick()
        self.threshold += self.clock.get_time()
        # if there is no threshold here, it makes like a cool laser effect with lots of particles
        if self.threshold > self.freq:
            self.threshold = 0
            if self.target in creeps:
                d = self.target.pos - self.pos
                if d.length <= self.range:
                    p = Projectile(self.pos, self.target, self.upgrade)
                    p.vel = 10
                    p.color = self.color
                    particles_list.append(p)
                    pygame.time.set_timer(24, self.freq)
            else:
                self.target = 0
            
    def render(self, screen, grid):
        c = self.pos
        rect = [c[0]-grid.dx/2, c[1]-grid.dy/2, grid.dx-1, grid.dy-1]
        pygame.draw.rect(screen, self.color, rect)
        for i in xrange(self.upgrade):
            pygame.draw.line(screen, (0,75,0), (c[0]+6, c[1]+12-4*i), (c[0]+13, c[1]+12-4*i), 2)




# --- PARTICLE CLASSES ---

class Particle:
    def __init__(self):
        self.color = (0,0,0)
        self.pos = vec2d(0,0)
        self.vel = vec2d(0,0)
        self.life = 10
        
    def update(self, particles, creeps):
        self.pos += self.vel
        self.life -= 1
        if self.life == 0:
            particles.remove(self)
            
    def render(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]-1),int(self.pos[1]-1)), 2)
        

class Projectile:
    def __init__(self, pos, target, upgrade):
        self.pos = vec2d(pos)
        self.vel = 0
        self.dir = vec2d(0,0)
        self.color = (255,255,255)
        self.target = target
        self.upgrade = upgrade
        
    def update(self, particles_list, creeps):
        if self.target in creeps:
            self.dir = self.target.pos - self.pos
            if self.dir.length < 1.5*self.target.r:
                if self.target.hp >= 0:
                    self.target.hp -= 1
                particles_list.remove(self)
            self.dir.length = self.vel
            self.pos += self.dir
        else:
            particles_list.remove(self)
        
    def render(self, screen):
        pygame.draw.line(screen, self.color, self.pos, self.pos+self.dir, 1+self.upgrade)
    



# --- DATA CLASSES ---

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

    def checkNode(self, pos):
        p = self.getNode(pos)
        return self.Grid[p]

    def getNode(self, v):
        v = intvec(v)
        return ((v[0]+1)/self.dx, (v[1]+1)/self.dy)

    def getCoordinate(self, p):
        return vec2d(self.dx/2+self.dx*p[0], self.dy/2+self.dy*p[1])

    def insert(self, node, value):
        self.Grid[node] = value




class BinaryHeap:
    def __init__(self):
        self.heap = [0,[0,-1],[0,-1],[0,-1]]
        self.size = 0

    # node in form [(x, y), cost]
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




def Dijkstra(grid, source, target):
    D = {}
    S = []
    Q = BinaryHeap()

    maxn = grid.n
    maxm = grid.m
    for n in xrange(grid.n):
        for m in xrange(grid.m):
            if (n, m) == source:
                D[(n, m)] = (0, source)
            else:
                D[(n, m)] = (1000, 0)
    Q.insert([source, 0])
    while Q.size > 0:
        x = Q.remove_priority()
        if x[0] == target:
            break
        if x[1] == 1000:
            break
        S.insert(0, x[0])
        for i in [[1,0], [0,1], [-1,0], [0,-1]]:
            if maxn > x[0][0]+i[0] >= 0 and maxm > x[0][1]+i[1] >= 0:
                v = (x[0][0]+i[0], x[0][1]+i[1])
                if v not in S:
                    if grid.Grid[v] == 1:
                        dist = 1000
                    else:
                        dist = 1
                    d = D[x[0]][0] + dist
                    if d < D[v][0]:
                        D[v] = (d, x[0])
                        Q.insert([v, d])
    waypoints = [target]
    p = target
    while p != source:
        if p == 0:
            return [source]
        p = D[p][1]
        waypoints.insert(0, p)
    return waypoints




# --- PYGAME INIT CLASS ---

class Core(PygameHelper):
    def __init__(self):
        # set pygame vars
        self.w, self.h = 659, 659
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        self.background = pygame.image.load('img/abstract.jpg').convert()
        # init grid
        self.grid = Grid(20, 20, (self.w+1,self.h+1))
        # set grid where menu is to be occupied
        self.grid.Grid[(0,19)] = 1
        self.grid.Grid[(1,19)] = 1
        self.grid.Grid[(2,19)] = 1
        self.grid.Grid[(3,19)] = 1
        # pre-render numbers
        self.font = pygame.font.SysFont('Helvetica', 14, bold=False, italic=False)
        self.font2 = pygame.font.SysFont('Helvetica', 28, bold=True, italic=False)
        self.rendered_numbers = [0]
        for i in xrange(1,100):
            f = self.font.render(str(i), False, (0,0,0))
            self.rendered_numbers.append(f) 

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

