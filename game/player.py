from core import *


# global color dictionaries
global fill_colors
global highlight_colors
global RGBtoSTR
fill_colors = {'R':(255,0,0), 'G':(0,255,0), 'B':(0,0,255)}
highlight_colors = {'R':(255,100,100), 'G':(100,255,100), 'B':(100,100,255)}
RGBtoSTR = {(255,0,0):'R', (0,255,0):'G', (0,0,255):'B'}




class Base(Static):
    def render(self, screen, font):
        Static.render(self, screen, font)
        screen.blit(font.render("BASE", False, (0,0,0)), (self.pos[0]-self.w/2+1,self.pos[1]+self.h/2-13))



            
class Resource(Static):
    def __init__(self, rtype):
        shape = 'circle'
        w = 50
        fill = fill_colors[rtype]
        border = highlight_colors[rtype]
        self.rtype = rtype
        Static.__init__(self, shape, border, w, 0, fill)
        
    def render(self, screen, font):
        Static.render(self, screen, font)
        screen.blit(font.render(self.rtype, False, (0,0,0)), (self.pos[0]-6, self.pos[1]-7))




class Worker(Agent):
    def __init__(self):
        self.default_color = (150,150,150)
        self.default_selected_color = (200,200,200)
        r = 10
        vmax = 5
        Agent.__init__(self, self.default_color, self.default_selected_color, r, vmax)

        self.base_link = []
        self.resource_link = []
        self.inlink = False
        self.carrying = False

    def getLink(self, pos, resources, bases):
        resource = base = False
        for r in resources:
            if r.getOverlap(pos) == True:
                resource = True
                self.resource_link = [r]
                break
        for b in bases:
            if b.getOverlap(pos) == True:
                base = True
                self.base_link = [b]
                break
        if not resource and not base:
            self.base_link = []
            self.resource_link = []
            self.flying_class = False
            self.inlink = False

    def update(self, resource_dict):
        if len(self.base_link) > 0 and len(self.resource_link) > 0:
            if self.inlink == False:
                self.flying_class = True
                self.inlink = True
            if self.base_link[0].getOverlap(self.pos):
                self.carrying = False
                self.color = self.default_color
                self.selected_color = self.default_selected_color
                resource_dict[self.resource_link[0].fill_color] += 1
                self.waypoints = [self.resource_link[0].pos]
            if self.carrying == True:
                self.waypoints = [self.base_link[0].pos]
            if self.resource_link[0].getOverlap(self.pos):
                self.carrying = True
                c = RGBtoSTR[self.resource_link[0].fill_color]
                self.color = fill_colors[c]
                self.selected_color = highlight_colors[c]
                self.waypoints = [self.base_link[0].pos]
        Agent.update(self)

    def render_agent(self, screen, selected, font):
        Agent.render_agent(self, screen, selected, font)
        screen.blit(font.render("W", False, (0,0,0)), (self.pos[0]-6, self.pos[1]-7))




class Player(Core):
    def __init__(self):
        # REMINDER: need to append all statics and agents to self.statics and self.agents
        Core.__init__(self)

        self.workers = []
        self.resources = []
        self.bases = []
        self.resource_dict = {(255,0,0):0, (0,255,0):0, (0,0,255):0}

        for i in xrange(12):
            w = Worker()
            w.pos = vec2d(100+i*30,50)
            self.agents.append(w)
            self.workers.append(w)

        r = Resource('R')
        r.pos = vec2d(400,300)
        self.statics.append(r)
        self.resources.append(r)

        r = Resource('G')
        r.pos = vec2d(500,300)
        self.statics.append(r)
        self.resources.append(r)

        r = Resource('B')
        r.pos = vec2d(600,300)
        self.statics.append(r)
        self.resources.append(r)
        
        b = Base('rect', (0,0,0), 100, 100)
        b.pos = vec2d(500,500)
        self.statics.append(b)
        self.bases.append(b)

    def keyDown(self, key):
        Core.keyDown(self, key)

    def keyUp(self, key):
        Core.keyUp(self, key)

    def mouseUp(self, button, pos):
        Core.mouseUp(self, button, pos)
        if button == 3:
            # worker gathering link
            for w in self.workers:
                if w in self.selected:
                    w.getLink(pos, self.resources, self.bases)
                    
    def mouseMotion(self, buttons, pos, rel):
        Core.mouseMotion(self, buttons, pos, rel)

    def update(self):
        for a in self.agents:
            if a.__class__.__name__ == 'Worker':
                a.update(self.resource_dict)
            else:
                a.update()
        Core.update(self)

    def draw(self):
        self.screen.fill((255,255,255))
        Core.draw(self)
        score = "R: "+str(self.resource_dict[(255,0,0)])+" G: "+str(self.resource_dict[(0,255,0)])+ \
                " B: "+str(self.resource_dict[(0,0,255)])
        self.screen.blit(self.font.render(score, False, (0,0,0)), (5,5))




p = Player()
p.mainLoop(40)


