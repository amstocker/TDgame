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
default_tower = (101,255,102)
frost_tower = (102,254,236)
fire_tower = (235,52,82)
laser_tower = (91,52,235)





# --- MENU CLASSES ---

class Menu:
    def __init__(self, font, show=True):
        self.show = show
        self.font = font
        self.menutext = self.font.render("build", False, (255,255,255))
        
        # menu scrolling
        self.scrolling = False
        self.scroll_pos = 0
        self.extended = False
        self.h = 627
        self.scrollh = 33
        
        self.surface = pygame.Surface((131,131))
        self.surface.set_alpha(175)
        self.surface.convert()
        self.surface.fill((0,0,0))

        self.xoffset = 0

        self.itemlist = []
        self.item1 = Rect(4+self.xoffset, self.h+4, 24, 24)
        self.item2 = Rect(37+self.xoffset, self.h+4, 24, 24)
        self.item3 = Rect(70+self.xoffset, self.h+4, 24, 24)
        self.item4 = Rect(103+self.xoffset, self.h+4, 24, 24)
        self.itemlist.append(self.item1)
        self.itemlist.append(self.item2)
        self.itemlist.append(self.item3)
        self.itemlist.append(self.item4)

        self.selected = self.item1
        self.hovered = self.item1
        
    def getClick(self, pos):
        if self.extended == False and 132+self.xoffset >= pos[0] >= 0+self.xoffset \
          and 659 >= pos[1] >= self.h-2:
            self.scrolling = True
            return True
        elif self.extended == True and 132+self.xoffset >= pos[0] >= 0+self.xoffset \
          and 659 >= pos[1] >= self.h-2:
            self.getHover(pos, 1)
            self.scrolling = True
            return True
        else:
            return False

    def update(self):
        pass
        
    def getHover(self, pos, selected=0):
        if selected == 1:
            for item in self.itemlist:
                if item.collidepoint(pos) == True:
                    self.selected = item
        elif self.extended == True:
            for item in self.itemlist:
                if item.collidepoint(pos) == True:
                    self.hovered = item

    def scroll(self):
        if self.extended == False:
            if self.scroll_pos < self.scrollh:
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
        rect_outline = [0+self.xoffset-1, self.h-1, 133, 132]
        pygame.draw.rect(screen, (255,255,255), rect_outline, 1)
        screen.blit(self.surface, (0+self.xoffset,self.h))
        # draw outline around selected
        rect_selected = [self.selected.x-2, self.selected.y-2, self.selected.w+4, self.selected.h+4]
        pygame.draw.rect(screen, (255,255,255), rect_selected)
        # menu items
        self.item1.y = self.h+4
        self.item2.y = self.h+4
        self.item3.y = self.h+4
        self.item4.y = self.h+4
        pygame.draw.rect(screen, (101,255,102), self.item1)
        pygame.draw.rect(screen, (102,254,236), self.item2)
        pygame.draw.rect(screen, (235,52,82), self.item3)
        pygame.draw.rect(screen, (91,52,235), self.item4)
        # draw outline on hovered
        pygame.draw.rect(screen, (255,255,255), self.hovered, 2)
        # draw overlap for smooth scrolling
        rect_overlap = [0+self.xoffset, 628, 131, 31]
        pygame.draw.rect(screen, (0,0,0), rect_overlap)
        screen.blit(self.menutext, (5+self.xoffset, 629))
        




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
            
    def update(self, grid, creeps, particles_list, score):
        if self.hp <= 0:
            score += 1
            creeps.remove(self)
            for p in xrange(20):
                rdir = vec2d(uniform(-3,3), uniform(-3,3))
                p = Particle()
                p.color = self.color
                p.pos = (self.pos[0]+randint(-1,1),self.pos[1]+randint(-1,1))
                p.origin = (self.pos[0], self.pos[1])
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
        # waypoints
        for i in xrange(len(self.waypoints)):
            pygame.draw.circle(screen, self.color, grid.getCoordinate(self.waypoints[i]), 5, 1)
            if i+1 < len(self.waypoints):
                pygame.draw.line(screen, self.color, grid.getCoordinate(self.waypoints[i]), \
                                 grid.getCoordinate(self.waypoints[i+1]), 1)
        # creep
        pygame.draw.circle(screen, (0,0,0), intvec(self.pos), int(self.r)+1)
        pygame.draw.circle(screen, self.color, intvec(self.pos), int(self.r))
        pygame.draw.line(screen, (0,0,0), (self.pos[0]-self.r, self.pos[1]-self.r-5), \
                         (self.pos[0]+self.r, self.pos[1]-self.r-5), 5)
        # floating HP bar
        hplossratio = 1-float(self.hp)/self.maxhp
        pygame.draw.line(screen, (146,116,252), (self.pos[0]-self.r+1, self.pos[1]-self.r-5), \
                         (self.pos[0]+self.r-(hplossratio*1.8*self.r)-1, self.pos[1]-self.r-5), 3)





# --- TOWER CLASSES ---

class Tower:
    def __init__(self, grid, pos, freq=1000):
        self.node = grid.getNode(pos)
        self.pos = grid.getCoordinate(self.node)
        
        # timing
        self.freq = freq
        self.clock = pygame.time.Clock()
        self.threshold = 0
        
        self.target = 0
        self.color = (101,255,102)
        self.range = 200
        self.projectile_dmg = 10
        self.projectile_size = 3
        self.projectile_color = (151,255,152)
        self.projectile_shape = 'line'

        self.inrange = False
        self.firing = False

        # self.c = topleft corner of coordinate
        self.c = (self.pos[0]-grid.dx/2+2, self.pos[1]-grid.dy/2+2)
        self.rect = [self.c[0], self.c[1], grid.dx-5, grid.dy-5]
        
    def update(self, particles_list, creeps):
        self.clock.tick()
        self.threshold += self.clock.get_time()
        # if there is no threshold here, it makes like a cool laser effect with lots of particles,
        # perhaps use with slight randint variation in a cool blue/purple color?
        if self.threshold > self.freq:
            self.firing = True
        if self.inrange == False:
            for c in creeps:
                d = c.pos - self.pos
                if d.length <= self.range:
                    self.inrange = True
                    self.target = c
                    break
        else:
            if self.target in creeps:
                d = self.target.pos - self.pos
                if d.length <= self.range:
                    if self.firing == True:
                        self.firing = False
                        self.threshold = 0
                        p = Projectile(self.pos, self.target, self.projectile_dmg, self.projectile_size, self.projectile_shape)
                        p.vel = 10
                        p.color = self.projectile_color
                        particles_list.append(p)
            else:
                self.inrange = False
            
    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class DefaultTower(Tower):
    def __init__(self, grid, pos):
        Tower.__init__(self, grid, pos)
    def update(self, particles_list, creeps):
        if self.inrange == True and self.firing == True:
            self.color = (200,255,200)
        else:
            self.color = (101,255,102)
        Tower.update(self, particles_list, creeps)


class LaserTower(Tower):
    def __init__(self, grid, pos):
        Tower.__init__(self, grid, pos)
        self.color = (91,52,235)
        self.range = 100
        self.freq = 0
        self.projectile_dmg = 3
        self.projectile_size = 4
        self.projectile_color = (91,52,235)
    def update(self, particles_list, creeps):
        if self.inrange == True:
            r = (91+randint(-90,90),52+randint(-50,50),235+randint(-20,20))
            self.projectile_color = r
            self.color = r
        else:
            self.color = (91,52,235)
        Tower.update(self, particles_list, creeps)


class FireTower(Tower):
    def __init__(self, grid, pos):
        Tower.__init__(self, grid, pos)
        self.color = (235,52,82)
        self.freq = 2500
        self.range = 350
        self.projectile_dmg = 50
        self.projectile_size = 8
        self.projectile_color = (235,150,180)
        self.projectile_shape = 'ball'
        




# --- PARTICLE CLASSES ---

class Particle:
    def __init__(self):
        self.color = (0,0,0)
        self.pos = vec2d(0,0)
        self.origin = vec2d(0,0)
        self.vel = vec2d(0,0)
        self.life = randint(20,50)
        
    def update(self, particles, creeps):
        self.pos += self.vel
        self.life -= 1
        if self.life == 0:
            particles.remove(self)
            
    def render(self, screen):
        pygame.draw.line(screen, self.color, self.origin, self.pos, 1)
        pygame.draw.circle(screen, self.color, (int(self.pos[0]-1),int(self.pos[1]-1)), 2)
        

class Projectile:
    def __init__(self, pos, target, dmg, size, shape='line'):
        self.pos = vec2d(pos)
        self.vel = 0
        self.dir = vec2d(0,0)
        self.color = (255,255,255)
        self.target = target
        self.dmg = dmg
        self.size = size
        self.shape = shape
        
    def update(self, particles_list, creeps):
        if self.target in creeps:
            self.dir = self.target.pos - self.pos
            if self.dir.length < 1.5*self.target.r:
                if self.target.hp >= 0:
                    self.target.hp -= self.dmg
                particles_list.remove(self)
            self.dir.length = self.vel
            self.pos += self.dir
        else:
            particles_list.remove(self)
        
    def render(self, screen):
        if self.shape == 'line':
            pygame.draw.line(screen, self.color, self.pos, self.pos+self.dir, 1+self.size)
        if self.shape == 'ball':
            pygame.draw.circle(screen, self.color, intvec(self.pos), self.size)
    



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
        self.background = pygame.image.load('img/space_new.jpg').convert()
        # init grid
        self.grid = Grid(20, 20, (self.w+1,self.h+1))
        # set grid to occupied at creep spawn, space station, and menu
        self.grid.Grid[(0,19)] = 1
        self.grid.Grid[(1,19)] = 1
        self.grid.Grid[(2,19)] = 1
        self.grid.Grid[(3,19)] = 1
        for i in xrange(10):
            self.grid.Grid[(i,0)] = 1
        for i in xrange(1,10):
            self.grid.Grid[(0,i)] = 1
        # pre-render numbers
        self.font = pygame.font.SysFont('Helvetica', 14, bold=False, italic=False)
        self.font2 = pygame.font.SysFont('Helvetica', 24, bold=False, italic=False)
        self.rendered_numbers = [0]
        for i in xrange(1,100):
            f = self.font.render(str(i), False, (0,0,0))
            self.rendered_numbers.append(f)
            
        self.target_blocked = False
            
    def spawnRandomCreep(self):
        C = Creep((randint(220,255), randint(0,50), randint(50,100)), 10, 4, 100)
        side = randint(0,1)
        pos = (side*randint(0,9),(1-side)*randint(0,9))
        C.pos = self.grid.getCoordinate(pos)
        target = 0
        for i in [0, 1]:
            for j in range(4):
                t = (i*(16+j),(1-i)*(16+j))
                if self.grid.Grid[t] == 0:
                    target = t
        if target == 0:
            self.blocked = True
        C.waypoints = Dijkstra(self.grid, pos, (17,17))
        self.creeps.append(C)

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

