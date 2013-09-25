from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform

# convert vec2d elements into integers
def intvec(v):
    return vec2d(int(v.x), int(v.y))




class Agent:
    def __init__(self, r):
        self.pos = vec2d(0,0)
        self.waypoints = []
        self.r = r
        self.grav = 0
        
    def render(self, screen, selected, loop):
        pygame.draw.circle(screen, (0,0,0), intvec(self.pos), int(self.r)+1)
        # draw agent
        if self in selected:
            pygame.draw.circle(screen, (0,175,255), intvec(self.pos), int(self.r))
        else:
            pygame.draw.circle(screen, (0,100,255), intvec(self.pos), int(self.r))
        # draw waypoint(s)
        for i in xrange(len(self.waypoints)):
            pygame.draw.circle(screen, (255,50,0), intvec(self.waypoints[i]), 30, 1)
            if i+1 < len(self.waypoints):
                pygame.draw.line(screen, (255,50,0), intvec(self.waypoints[i]), intvec(self.waypoints[i+1]), 1)
                
    def update(self, loop):
        dir = self.waypoints[0] - self.pos
        if dir.length > (self.r+30):
            dir.length = max(7.5, dir.length*0.04)
            self.pos += dir
        elif len(self.waypoints) > 1:
            if loop == True:
                temp = self.waypoints[0]
                self.waypoints.append(temp)
            self.waypoints.pop(0)
        elif 3 < dir.length <= (self.r+30):
            dir.length *= 0.15
            self.pos += dir

    def detect_static_collision(self, static):
        dir = static.collision_vector(self)
        if dir != 0 and dir.length > 2:
            self.pos += dir
            
    def detect_self_collision(self, other):
        d = self.pos.get_distance(other.pos)
        if d < (self.r+other.r):
            overlap = (self.r+other.r)-d
            dir = other.pos - self.pos
            dir.length = int(overlap)/2
            other.pos += dir
            self.pos -= dir
##          *EXPERIMENTAL COLLISION
##          dir.length = int(overlap)
##          self.pos -= dir




class Static:
    # types are 'rect' or 'circle' (for now), if type is circle: d = w
    def __init__(self, shape, color, w, h=1):
        self.pos = vec2d(0,0)
        self.shape = shape
        self.color = color
        self.w = w
        self.h = h

    def render(self, screen):
        if self.shape == 'circle':
            pygame.draw.circle(screen, self.color, intvec(self.pos), int(self.w*0.5), 2)
        elif self.shape == 'rect':
            rect = [(self.pos[0]-(self.w/2)), (self.pos[1]-(self.h/2)), self.w, self.h]
            pygame.draw.rect(screen, self.color, rect, 2)

    def collision_vector(self, other):
        # find vector with which to offset other collided object
        if self.shape == 'circle':
            d = self.pos.get_distance(other.pos)
            if d < (self.w+other.r):
                dir = other.pos - self.pos
                dir.length = (self.w+other.r)
                return dir
            else:
                return 0
        if self.shape == 'rect':
            dx, dy = (self.w*0.5+other.r), (self.h*0.5+other.r)
            d = other.pos-self.pos
            if abs(d[0])<dx and abs(d[1])<dy:
                if dx-abs(d[0]) < dy-abs(d[1]):
                    dir = vec2d(d[0],0)
                    dir.length = int(dx-abs(d[0]))
                    return dir
                elif dx-abs(d[0]) > dy-abs(d[1]):
                    dir = vec2d(0,d[1])
                    dir.length = int(dy-abs(d[1]))
                    return dir
            else:
                return 0




class Core(PygameHelper):
    def __init__(self, particles):
        # set pygame vars
        self.w, self.h = 1024, 768
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        self.font=pygame.font.SysFont(None, 20, bold=False, italic=False)
        # mouse cursor
        self.pos = (0,0)

        # initialize agents at random positions
        self.agents = []
        for i in xrange(particles):
            a = Agent(10)
            a.pos = vec2d(uniform(self.w*0.1,self.w*0.9), uniform(self.h*0.1,self.h*0.9))
            a.waypoints.append(vec2d(uniform(self.w*0.1,self.w*0.9), uniform(self.h*0.1,self.h*0.9)))
            self.agents.append(a)
        self.selected = [self.agents[0]]

        # initialize static objects
        self.statics = []

        # control group toggle/dictionary
        self.lctrl = False
        self.ctrl_groups = {}

        # loop toggle
        self.loop = False

        # show_controls toggle
        self.show_controls = False
        # draw_static toggles
        self.static_draw = False
        self.newstatic = False
        # LSHIFT toggle
        self.add_waypoints = False
        # dragbox_draw toggle
        self.dragbox_draw = False
        # dragbox coordinates
        self.dragbox_origin = vec2d(0,0)
        self.dragbox_pos = vec2d(0,0)

        # web toggle
        self.show_web = False
        
    def update(self):
        for a in self.agents:
            a.update(self.loop)
##      *trying different types of collision detection
##      *commented out is old solution, better for fewer agents w/ larger radii and looks cleaner
##      for a in self.agents:
##          for a2 in self.agents:
##              if a == a2:
##                  continue
##              a.detect_self_collision(a2)
        for a in xrange(len(self.agents)):
            for a2 in xrange(a+1, len(self.agents)):
                self.agents[a].detect_self_collision(self.agents[a2])
        for s in self.statics:
            for a in self.agents:
                a.detect_static_collision(s)

    def keyDown(self, key):
        if key == K_w:
            self.show_web = not self.show_web
        if key == K_e:
            self.loop = not self.loop
        if key == K_s:
            self.static_draw = True
        if key == K_LSHIFT:
            self.add_waypoints = True
        if key == K_LCTRL:
            self.lctrl = True
        # assign control groups
        if self.lctrl == True and 48 <= key <= 57:
            self.ctrl_groups[key] = self.selected
        elif key in self.ctrl_groups.keys():
            self.selected = self.ctrl_groups[key]
        # select all (LCTRL+A)
        if self.lctrl == True and key == K_a:
            self.selected = self.agents
                
    
    def keyUp(self, key):
        # reset static objects
        if key == K_r:
            if self.dragbox_draw == False and self.static_draw == False:
                self.statics = []
        if key == K_s:
            self.static_draw = False
        if key == K_LSHIFT:
            self.add_waypoints = False
        if key == K_LCTRL:
            self.lctrl = False
        # disperse function (LSHIFT+D)
        if self.add_waypoints and key == K_d:
            for a in self.selected:
                a.waypoints = [vec2d(uniform(self.w*0.1,self.w*0.9), uniform(self.h*0.1,self.h*0.9))]
        
    def mouseUp(self, button, pos):
        # show controls toggle
        if self.dragbox_draw == False and self.static_draw == False and button == 1 and \
           2<pos[0]<192 and 23<pos[1]<37:
            self.show_controls = not self.show_controls
        # if LSHIFT:
        # left mouse button click appends to selected list
        # right mouse button click appends to waypoint list
        elif self.add_waypoints == True:
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
            if self.dragbox_draw == False and self.static_draw == False:
                for a in self.agents:
                    if a.pos.get_distance(vec2d(pos)) <= 20:
                        self.selected = [a]
            self.newstatic = False
            self.dragbox_draw = False
        elif button == 3:
            for a in self.selected:
                a.waypoints = [vec2d(pos)]
        
    def mouseMotion(self, buttons, pos, rel):
        self.pos = pos
        if buttons[0] == 1:
            # static drawing logic
            if self.static_draw == True and self.newstatic == False:
                self.newstatic = True
                self.dragbox_origin = self.dragbox_pos = vec2d(pos)
                s = Static('rect', (0,255,175), 5, 5)
                s.pos = self.dragbox_origin
                self.statics.append(s)
            elif self.static_draw == True and self.newstatic == True:
                self.dragbox_pos = vec2d(pos)
                s = self.statics[len(self.statics)-1]
                d = self.dragbox_pos-self.dragbox_origin
                s.pos = vec2d(self.dragbox_origin[0]+d[0]/2, self.dragbox_origin[1]+d[1]/2)
                s.w = abs(d[0])
                s.h = abs(d[1])
            # dragbox logic
            elif self.dragbox_draw == False and self.static_draw == False:
                self.dragbox_draw = True
                self.dragbox_origin = self.dragbox_pos = vec2d(pos)
            elif self.dragbox_draw == True:
                self.dragbox_pos = vec2d(pos)
                # append boxed units to selection if LSHIFT is held down
                # if LSHIFT not held down, create new selection
                if not self.add_waypoints:
                    self.selected = []
            # if agent is in range of the dragbox (determined at center of agent: a.pos)
            if self.static_draw == False:
                for a in self.agents:
                    if a not in self.selected:
                        if self.dragbox_origin[0] <= a.pos[0] <= self.dragbox_pos[0] or \
                           self.dragbox_origin[0] >= a.pos[0] >= self.dragbox_pos[0]:
                            if self.dragbox_origin[1] <= a.pos[1] <= self.dragbox_pos[1] or \
                               self.dragbox_origin[1] >= a.pos[1] >= self.dragbox_pos[1]:
                                    self.selected.append(a)
        # drag waypoint
        if buttons[2] == 1 and not self.add_waypoints:
            for a in self.selected:
                a.waypoints = [vec2d(pos)]
        
    def draw(self):
        # draw background image
        self.screen.fill((255,255,255))
        # render statics
        for s in self.statics:
            s.render(self.screen)
        # render agents
        for a in self.agents:
            a.render(self.screen, self.selected, self.loop)
        if self.show_web == True:
            for a in xrange(len(self.agents)):
                for a2 in xrange(a+1, len(self.agents)):
                    pygame.draw.line(self.screen, (0,0,0), self.agents[a].pos, self.agents[a2].pos, 1)
        # draw dragbox
        if self.dragbox_draw == True and self.static_draw == False:
            dim = self.dragbox_pos-self.dragbox_origin
            rect = [self.dragbox_origin[0], self.dragbox_origin[1], dim[0], dim[1]]
            pygame.draw.rect(self.screen, (0,255,50), rect, 1)
        # controls text
        pos = '('+str(self.pos[0])+','+str(self.pos[1])+')'
        self.screen.blit(self.font.render(pos, False, (0,0,0)), (5,5))
        if self.show_controls == True:
            self.screen.blit(self.font.render("click here to hide", False, (0,0,0)), (5,25))
            self.screen.blit(self.font.render("LEFT-MOUSE-BUTTON to select, drag mouse to box-select", False, (0,0,0)), (5,42))
            self.screen.blit(self.font.render("RIGHT-MOUSE-BUTTON to set waypoint, hold to drag waypoint", False, (0,0,0)), (5,54))
            self.screen.blit(self.font.render("hold LSHIFT to queue waypoint(s) or add to selection", False, (0,0,0)), (5,66))
            self.screen.blit(self.font.render("pres LSHIFT+D to shuffle selected", False, (0,0,0)), (5,78))
            self.screen.blit(self.font.render("drag while holding S to create static objects", False, (0,0,0)), (5,90))
            self.screen.blit(self.font.render("press R to reset static objects", False, (0,0,0)), (5,102))
            self.screen.blit(self.font.render("hold LCTRL and a number key to assign control groups", False, (0,0,0)), (5,114))
        else:
            self.screen.blit(self.font.render("click here to show controls", False, (0,0,0)), (5,25))
        if self.loop == True:
            self.screen.blit(self.font.render('LOOP', False, (0,0,0)), (980,5))



            
c = Core(100)
c.mainLoop(40)
