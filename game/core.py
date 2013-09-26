from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform




# convert vec2d elements into integers (copyright Bill Cauchois 2013)
def intvec(v):
    return vec2d(int(v.x), int(v.y))




class Agent:
    def __init__(self, color, selected_color, r, vmax):
        self.color = color
        self.selected_color = selected_color
        self.r = r
        self.vmax = vmax

        self.pos = vec2d(0,0)
        self.waypoints = []
        
        # waypoint loop toggle
        self.loop = False

        # units with flying_class = True will only collide with eachother and nothing else
        self.flying_class = False
        
    def render_agent(self, screen, selected, font):
        pygame.draw.circle(screen, (0,0,0), intvec(self.pos), int(self.r)+1)
        if self in selected:
            pygame.draw.circle(screen, self.selected_color, intvec(self.pos), int(self.r))
        else:
            pygame.draw.circle(screen, self.color, intvec(self.pos), int(self.r))

    def render_agent_waypoints(self, screen):
        for i in xrange(len(self.waypoints)):
            pygame.draw.circle(screen, self.color, intvec(self.waypoints[i]), 10, 1)
            if i+1 < len(self.waypoints):
                pygame.draw.line(screen, self.color, intvec(self.waypoints[i]), intvec(self.waypoints[i+1]), 1)

    def detect_static_collision(self, static):
        if self.flying_class == True:
            return 0
        dir = static.collision_vector(self)
        if dir.length > 2:
            self.pos += dir
            
    def detect_self_collision(self, other):
        d = self.pos.get_distance(other.pos)
        if d < (self.r+other.r):
            overlap = (self.r+other.r)-d
            dir = other.pos - self.pos
            dir.length = int(overlap)/2
            other.pos += dir
            self.pos -= dir
            
    def update(self):
        if len(self.waypoints) > 0:
            dir = self.waypoints[0] - self.pos
            if dir.length > (self.r+5):
                dir.length = self.vmax
                self.pos += dir
            elif len(self.waypoints) > 1:
                if self.loop == True:
                    temp = self.waypoints[0]
                    self.waypoints.append(temp)
                self.waypoints.pop(0)
            elif 3 < dir.length <= (self.r+5):
                dir.length *= 0.15
                self.pos += dir




class Static:
    # types = ['rect', 'circle']
    # circle type uses self.w as diameter
    def __init__(self, shape, border_color, w, h=0, fill_color=(255,255,255)):
        self.pos = vec2d(0,0)
        self.shape = shape
        self.border_color = border_color
        self.w = w
        self.h = h
        self.fill_color = fill_color

    def render(self, screen, font):
        if self.shape == 'circle':
            pygame.draw.circle(screen, self.border_color, intvec(self.pos), self.w/2+2)
            pygame.draw.circle(screen, self.fill_color, intvec(self.pos), self.w/2)
        elif self.shape == 'rect':
            outline_rect = [(self.pos[0]-(self.w/2))-2, (self.pos[1]-(self.h/2))-2, self.w+4, self.h+4]
            fill_rect = [(self.pos[0]-(self.w/2)), (self.pos[1]-(self.h/2)), self.w, self.h]
            pygame.draw.rect(screen, self.border_color, outline_rect)
            pygame.draw.rect(screen, self.fill_color, fill_rect)

    def collision_vector(self, other):
        # find vector with which to offset collided object
        if self.shape == 'circle':
            d = self.pos.get_distance(other.pos)
            if d < (self.w/2+other.r):
                dir = other.pos - self.pos
                dir.length = (self.w/2+other.r)-d
                return dir
            else:
                return vec2d(0,0)
        if self.shape == 'rect':
            dx, dy = (self.w*0.5+other.r), (self.h*0.5+other.r)
            d = other.pos-self.pos
            if abs(d[0])<dx and abs(d[1])<dy:
                if dx-abs(d[0]) < dy-abs(d[1]):
                    dir = vec2d(d[0],0)
                    dir.length = dx-abs(d[0])
                    return dir
                elif dx-abs(d[0]) > dy-abs(d[1]):
                    dir = vec2d(0,d[1])
                    dir.length = dy-abs(d[1])
                    return dir
            else:
                return vec2d(0,0)

    def getOverlap(self, pos):
        # pos is vec2d object
        if self.shape == 'circle':
            d = pos-self.pos
            if d.length <= self.w/2:
                return True
        if self.shape == 'rect':
            if (self.pos[0]-self.w/2 <= pos[0] <= self.pos[0]+self.w/2):
                if (self.pos[1]-self.h/2 <= pos[1] <= self.pos[1]+self.h/2):
                    return True
        else:
            return False




class Projectile:
    pass




class Core(PygameHelper):
    def __init__(self):
        # set pygame vars
        self.w, self.h = 1024, 768
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        self.font=pygame.font.SysFont(None, 20, bold=False, italic=False)
        
        # mouse cursor
        self.pos = (0,0)

        # selected agents list
        self.selected = []

        # object lists
        self.agents = []
        self.statics = []

        # control group toggle/dictionary
        self.lctrl = False
        self.ctrl_groups = {}

        # LSHIFT toggle
        self.add_waypoints = False
        
        # dragbox_draw toggle
        self.dragbox_draw = False
        
        # dragbox coordinates
        self.dragbox_origin = vec2d(0,0)
        self.dragbox_pos = vec2d(0,0)

    def keyDown(self, key):
        if key == K_LSHIFT:
            self.add_waypoints = True
        if key == K_LCTRL:
            self.lctrl = True
        # assign control groups
        if self.lctrl == True and 48 <= key <= 57:
            self.ctrl_groups[key] = self.selected
        elif key in self.ctrl_groups.keys():
            self.selected = self.ctrl_groups[key]
                
    def keyUp(self, key):
        if key == K_LSHIFT:
            self.add_waypoints = False
        if key == K_LCTRL:
            self.lctrl = False
        
    def mouseUp(self, button, pos):
        # if LSHIFT:
        # left mouse button click appends to selected list
        # right mouse button click appends to waypoint list
        if self.add_waypoints == True:
            if button == 1:
                for a in self.agents:
                    if a not in self.selected and a.pos.get_distance(vec2d(pos)) <= 20:
                        self.selected.append(a)
                self.dragbox_draw = False
            elif button == 3:
                for a in self.selected:
                    a.waypoints.append(vec2d(pos))
        # if not LSHIFT:
        # left mouse button click on an agent, overrides selected list and creates new selection
        # right mouse button click overrides waypoint list and creates new waypoint
        elif button == 1:
            if self.dragbox_draw == False:
                for a in self.agents:
                    if a.pos.get_distance(vec2d(pos)) <= 20:
                        self.selected = [a]
            self.dragbox_draw = False
        elif button == 3:
            for a in self.selected:
                a.waypoints = [vec2d(pos)]
        
    def mouseMotion(self, buttons, pos, rel):
        self.pos = pos
        # dragbox logic
        if buttons[0] == 1:
            if self.dragbox_draw == False:
                self.dragbox_draw = True
                self.dragbox_origin = self.dragbox_pos = vec2d(pos)
            elif self.dragbox_draw == True:
                self.dragbox_pos = vec2d(pos)
                # append boxed units to selection if LSHIFT is held down
                # if LSHIFT not held down, create new selection
                if not self.add_waypoints:
                    self.selected = []
            # if agent is in range of the dragbox
            for a in self.agents:
                if a not in self.selected:
                    r = int(a.r*0.7)
                    if self.dragbox_origin[0]-r <= a.pos[0] <= self.dragbox_pos[0]+r or \
                       self.dragbox_origin[0]+r >= a.pos[0] >= self.dragbox_pos[0]-r:
                        if self.dragbox_origin[1]-r <= a.pos[1] <= self.dragbox_pos[1]+r or \
                           self.dragbox_origin[1]+r >= a.pos[1] >= self.dragbox_pos[1]-r:
                                self.selected.append(a)
        # drag waypoint
        if buttons[2] == 1 and not self.add_waypoints:
            for a in self.selected:
                a.waypoints = [vec2d(pos)]

    def update(self):
##      **alternate collision detection**        
##        for a in xrange(len(self.agents)):
##            for a2 in xrange(a+1, len(self.agents)):
##                if self.agents[a].flying_class == self.agents[a2].flying_class:
##                    self.agents[a].detect_self_collision(self.agents[a2])      
        for a in self.agents:
            for a2 in self.agents:
                if a == a2:
                    continue
                elif a.flying_class == a2.flying_class:
                    a.detect_self_collision(a2)
        for s in self.statics:
            for a in self.agents:
                a.detect_static_collision(s)
        
    def draw(self):
        for s in self.statics:
            s.render(self.screen, self.font)
        for a in self.agents:
            a.render_agent_waypoints(self.screen)
        for a in self.agents:
            a.render_agent(self.screen, self.selected, self.font)
        if self.dragbox_draw == True:
            dim = self.dragbox_pos-self.dragbox_origin
            rect = [self.dragbox_origin[0], self.dragbox_origin[1], dim[0], dim[1]]
            pygame.draw.rect(self.screen, (0,255,50), rect, 1)



            
