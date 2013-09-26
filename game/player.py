from core import *


class HQ(Static):
    def __init__(self):
        Static.__init__(self, 'rect', (0,0,0), 250, 120)
        self.hq_img = pygame.image.load('img/HQ.jpeg').convert()

        self.pos = vec2d(582,65)

        # menu display toggle
        self.display_menu = False

    def update(self, pos, agents, workers):
        if self.display_menu == True:
            w = Worker()
            w.pos = vec2d(self.pos[0], self.pos[1]+60+w.r+10)
            workers.append(w)
            agents.append(w)
            w.waypoints = [vec2d(582, 200)]
            self.display_menu = False
            
    def render(self, screen, font):
        Static.render(self, screen, font)
        screen.blit(self.hq_img, (self.pos[0]-self.w/2, self.pos[1]-self.h/2))
        pygame.draw.rect(screen, (0,0,0), [(self.pos[0]-self.w/2), (self.pos[1]-self.h/2), self.w, 24])
        screen.blit(font.render("Headquarters", False, (255,255,255)), (self.pos[0]-self.w/2+148, self.pos[1]-self.h/2+1))



            
class Ammunition(Static):
    def __init__(self):
        Static.__init__(self, 'rect', (0,0,0), 150, 100)
        self.ammo_img = pygame.image.load('img/bullets.jpeg').convert()

        self.rtype = 'Ammunition'
        self.color = (247,73,49)
        self.selected_color = (255,152,97)
        
        self.pos = vec2d(375,55)
        self.inventory = 0

        # menu display toggle
        self.display_menu = False
        
    def render(self, screen, font):
        Static.render(self, screen, font)
        screen.blit(self.ammo_img, (self.pos[0]-self.w/2, self.pos[1]-self.h/2))
        pygame.draw.rect(screen, (0,0,0), [(self.pos[0]-self.w/2), (self.pos[1]-self.h/2), self.w, 24])
        screen.blit(font.render("Ammunition", False, (255,255,255)), (self.pos[0]-self.w/2+60, self.pos[1]-self.h/2+1))
        screen.blit(font.render(str(int(self.inventory)), False, (255,255,255)), (self.pos[0]-self.w/2+1, self.pos[1]-self.h/2+1))



class Worker(Agent):
    def __init__(self):
        self.default_color = (175,175,175)
        self.default_selected_color = (225,225,225)
        r = 10
        vmax = 5
        Agent.__init__(self, self.default_color, self.default_selected_color, r, vmax)
        self.font2 = pygame.font.SysFont('Helvetica', 14, bold=False, italic=False)

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
                return
        for b in bases:
            if b.getOverlap(pos) == True:
                base = True
                self.base_link = [b]
                return
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
                self.resource_link[0].inventory -= 1
                self.waypoints = [self.resource_link[0].pos]
            if self.carrying == True:
                self.waypoints = [self.base_link[0].pos]
            if self.resource_link[0].getOverlap(self.pos):
                self.carrying = True
                self.color =  self.resource_link[0].color
                self.selected_color = self.resource_link[0].selected_color
                self.waypoints = [self.base_link[0].pos]
        Agent.update(self)

    def render_agent(self, screen, selected):
        if len(self.waypoints) > 0:
            pygame.draw.line(screen, self.color, intvec(self.pos), intvec(self.waypoints[0]), 1)
        Agent.render_agent(self, screen, selected)
        screen.blit(self.font2.render("W", False, (0,0,0)), (self.pos[0]-7, self.pos[1]-7))




class Player(Core):
    def __init__(self):
        # REMINDER: need to append all statics and agents to self.statics and self.agents
        # for collision calculations.  Agent class has .flying_class boolean such for which
        # units with flying_class = True will only collide with eachother and nothing else.
        Core.__init__(self)
        self.bground = pygame.image.load('img/ground_texture.jpeg').convert()

        self.workers = []
        self.resources = []
        self.bases = []
        
        self.resource_dict = {'Ammunition':0}
        
        self.ammo = Ammunition()
        self.statics.append(self.ammo)
        self.resources.append(self.ammo)

        self.hq = HQ()
        self.statics.append(self.hq)
        self.bases.append(self.hq)

    def keyDown(self, key):
        Core.keyDown(self, key)

    def keyUp(self, key):
        Core.keyUp(self, key)

    def mouseUp(self, button, pos):
        Core.mouseUp(self, button, pos)
        if button == 1:
            for s in self.statics:
                if s.getOverlap(pos):
                    s.display_menu = True
                else:
                    s.display_menu = False
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
        self.hq.update(self.pos, self.agents, self.workers)
        self.ammo.inventory += 0.05
        Core.update(self)

    def draw(self):
        self.screen.blit(self.bground, (0,0))
        Core.draw(self)
        #pygame.draw.polygon(self.screen, (0,0,0), [(100,200), (150,300), (100,400)])




p = Player()
p.mainLoop(40)


