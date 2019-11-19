import pygame, math, sys

def dist(object1, object2):
    r = [object2.cx - object1.cx, object2.cy - object1.cy]
    magnitude = (r[0]**2 + r[1]**2)**0.5
    rUnit = [r[0]/magnitude, r[1]/magnitude]
    return [rUnit, magnitude]

# pass in cx, cy, always starts at r = 0/1 and grows as mouse is held
class Planet(object):
    def __init__(self, pos):
        self.cx, self.cy = pos[0], pos[1]
        self.r = 0
        self.mass = 0

# pass in cx, cy
class Enemy(object):
    def __init__(self, pos):
        self.cx, self.cy = pos[0], pos[1]
        self.r = 10
        self.velocity = [0,0]
        self.mass = 10
    
    def move(self, time):
        self.cx += self.velocity[0] * time
        self.cy += self.velocity[1] * time

class NovaGame(object):
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height))
        self.objects = []
        self.planets = []
        self.planetDensity = 10**4 # arbitrary value for now
        self.G = 6.7 * (10**-11)
        self.clock = pygame.time.Clock()
        self.growRate = 0.2
        pygame.display.set_caption('Midterm Dots')
        self.running = True
        self.currentPlanet = [None, False]

    def updatePhysics(self):
        for planet in self.planets:
            for enemy in self.objects:
                r = dist(enemy, planet)
                acceleration = (self.G * planet.mass) / (r[1])
                vector = [r[0][0] * acceleration, r[0][1] * acceleration]
                enemy.velocity[0] += vector[0]
                enemy.velocity[1] += vector[1]
    
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE:
                    if len(self.planets) > 0:
                        self.planets.pop()
                if event.key == pygame.K_p:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    self.currentPlanet = [Planet(pygame.mouse.get_pos()), True]
                    self.planets.append(self.currentPlanet[0])
                elif pygame.mouse.get_pressed()[2]:
                    self.objects.append(Enemy(pygame.mouse.get_pos()))
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.currentPlanet[1]:
                    self.currentPlanet[1] = False
                    self.currentPlanet[0].mass = (2 * math.pi * 
                    (self.currentPlanet[0].r**2) * self.planetDensity)
            elif event.type == pygame.QUIT:
                sys.exit()

    def checkCollisions(self):
        newObjects = self.objects
        for planet in self.planets:
            for enemy in self.objects:
                if dist(planet, enemy)[1] <= planet.r:
                    newObjects.remove(enemy)
        self.objects = newObjects

    def play(self):
        while self.running:
            self.screen.fill([255,255,255])
            self.checkEvents()
            self.checkCollisions()
            self.updatePhysics()
            if self.currentPlanet[1]:
                self.currentPlanet[0].r += self.growRate * self.clock.get_time()
                self.currentPlanet[0].mass = (2 * math.pi * 
                (self.currentPlanet[0].r**2) * self.planetDensity)
            for enemy in self.objects:
                enemy.move(self.clock.get_time())
                pygame.draw.circle(self.screen, [127, 127, 127], (enemy.cx, enemy.cy), enemy.r)
            for planet in self.planets:
                pygame.draw.circle(self.screen, [255,0,0], (planet.cx, planet.cy), planet.r)
            self.clock.tick()
            pygame.display.flip()

def runNovaGame():
    pygame.init()
    game = NovaGame(width = 800, height = 800)
    game.play()