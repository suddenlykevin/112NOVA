#################################################
# NOVA TP1 Deliverable
#
# Your name: Kevin Xie
# Your andrew id: kevinx
#################################################

import pygame, math, sys
import random
from PIL import Image

# applies distance formula to two objects given cx and cyrun
def dist(object1, object2):
    r = [object2.cx - object1.cx, object2.cy - object1.cy]
    magnitude = (r[0]**2 + r[1]**2)**0.5
    rUnit = [r[0]/magnitude, r[1]/magnitude]
    return [rUnit, magnitude]

# holds player position and attributes
class Player(object):
    def __init__(self, screen, pos):
        self.screen = screen
        self.cx, self.cy = pos[0], pos[1]
        self.fuel = 10**6

    def drawGUI(self):
        ratio = self.fuel / 10**6
        fuelBar = pygame.Rect(0, self.screen.get_height() - 10, 
                       self.screen.get_width() * ratio, 10)
        pygame.draw.rect(self.screen, [255,127,0], fuelBar)
    
    def draw(self):
        pass

    def retrieveSprites(self):
        spritesheet = Image.open("4Njmyen.png")
        dx, dy = 96, 104
        # 8 animations, each with a maximum of 10 frames
        spriteAnims = 8
        maxFrames = 10
        sprites = []
        # splits animation into 8 strips
        for strip in range(spriteAnims):
            spritestrip = []
            for i in range(maxFrames):
                spritestrip.append(spritesheet.crop((dx*i, dy*strip,
                                                     dx*(i+1), dy*(strip+1))))
            sprites.append(spritestrip)
        # scales each sprite down by half
        for row in range(spriteAnims):
            for col in range(maxFrames):
                sprites[row][col] = sprites[row][col].resize(48, 52)
        return sprites

# pass in cx, cy, always starts at r = 0/1 and grows as mouse is held
class Planet(object):
    def __init__(self, screen, pos):
        self.screen = screen
        self.cx, self.cy = pos[0], pos[1]
        self.r = 0
        self.mass = 0

    def draw(self):
        pass

# pass in cx, cy
class Enemy(object):
    def __init__(self, screen, pos):
        self.screen = screen
        self.cx, self.cy = pos[0], pos[1]
        self.r = 10
        self.velocity = [0,0]
        self.mass = 10
    
    def move(self, time):
        self.cx += self.velocity[0] * time
        self.cy += self.velocity[1] * time
    
    def draw(self):
        pass

# test subclass of enemy
class BadEnemey(Enemy):
    def __init__(self, screen, pos):
        super().__init__(screen, pos)

# main gameplay
class NovaGame(object):
    def __init__(self, screen, width, height):
        self.width, self.height = width, height
        self.screen = screen
        self.player = Player(self.screen, (10, 10))
        self.objects = []
        self.planets = []
        self.planetDensity = 10**4.5 # arbitrary value for now
        self.G = 6.7 * (10**-11)
        self.clock = pygame.time.Clock()
        self.timer = 100
        self.growRate = 0.2
        self.running = True
        self.currentPlanet = [None, False]

    # updates global physics acting on each planet -- maybe create vector field?
    def updatePhysics(self):
        # nested loop may become inefficient
        for planet in self.planets:
            for enemy in self.objects:
                r = dist(enemy, planet)
                acceleration = (self.G * planet.mass) / (r[1])
                vector = [r[0][0] * acceleration, r[0][1] * acceleration]
                enemy.velocity[0] += vector[0]
                enemy.velocity[1] += vector[1]
    
    # checks all "events" keystrokes, mousepresses etc.
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE:
                    if len(self.planets) > 0:
                        self.planets.pop()
                if event.key == pygame.K_p:
                    self.pause()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if not self.isInPlanet(pygame.mouse.get_pos()):
                        self.currentPlanet = [Planet(self.screen, pygame.mouse.get_pos()), True]
                        self.planets.append(self.currentPlanet[0])
                elif pygame.mouse.get_pressed()[2]:
                    self.objects.append(Enemy(self.screen, pygame.mouse.get_pos()))
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.currentPlanet[1]:
                    self.currentPlanet[1] = False
                    self.currentPlanet[0].mass = (2 * math.pi * 
                    (self.currentPlanet[0].r**2) * self.planetDensity)
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def isInPlanet(self, pos):
        for planet in self.planets:
            r = [planet.cx - pos[0], planet.cy - pos[1]]
            magnitude = (r[0]**2 + r[1]**2)**0.5
            if magnitude < planet.r:
                self.currentPlanet = [planet, True]
                return True
        return False

    def checkCollisions(self):
        newObjects = self.objects
        # nested loop may be inefficient
        for planet in self.planets:
            for enemy in self.objects:
                if dist(planet, enemy)[1] <= planet.r:
                    newObjects.remove(enemy)
                    self.player.fuel += enemy.mass * 10**4
                    if self.player.fuel > 10**6:
                        self.player.fuel = 10 ** 6
        self.objects = newObjects

    def pause(self):
        while self.running:
            self.screen.fill([255,255,255])
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        return

    def play(self):
        timerFont = pygame.font.Font('Linebeam.ttf', 24)
        while self.running:
            self.screen.fill([255,255,255])
            self.checkEvents()
            self.checkCollisions()
            self.updatePhysics()
            if self.currentPlanet[1] and self.player.fuel > self.growRate:
                self.currentPlanet[0].r += self.growRate * self.clock.get_time()
                self.currentPlanet[0].mass = (2 * math.pi * 
                (self.currentPlanet[0].r**2) * self.planetDensity)
                self.player.fuel -= self.growRate * self.planetDensity*4
            print(self.player.fuel)
            self.timer -= self.clock.get_time() * 10**-3
            for enemy in self.objects:
                enemy.move(self.clock.get_time())
                pygame.draw.circle(self.screen, [127, 127, 127], (enemy.cx, enemy.cy), enemy.r)
            for planet in self.planets:
                pygame.draw.circle(self.screen, [255,0,0], (planet.cx, planet.cy), planet.r)
            timer = timerFont.render(f'{int(self.timer)}', True, [0] * 3)
            timerSurface = timer.get_rect()
            timerSurface.center = ((self.width//2, self.height*1//5))
            self.screen.blit(timer, timerSurface)
            self.player.drawGUI()
            self.clock.tick()
            pygame.display.flip()

# Title/splashscreen
class TitleScreen(object):
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height))
        self.running = True
        self.game = NovaGame(self.screen, width, height)
        pygame.display.set_caption('NOVA')
    
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.game.play()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.game.play()
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def play(self):
        titleFont = pygame.font.Font('Linebeam.ttf', 48)
        littleFont = pygame.font.Font('Linebeam.ttf', 18)
        while self.running:
            self.checkEvents()
            self.screen.fill([255,255,255])
            titleText = titleFont.render('NOVA', True, [(pygame.time.get_ticks()//25) % 255] * 3)
            subTitle = littleFont.render('''PRESS ANYWHERE TO START GAME''', True, 
                                        [(pygame.time.get_ticks()//25) % 255] * 3)
            textSurface = titleText.get_rect()
            subSurface = subTitle.get_rect()
            subSurface.center = ((self.width//2, self.height*3//5))
            textSurface.center = ((self.width//2, self.height//2))
            self.screen.blit(titleText, textSurface)
            self.screen.blit(subTitle, subSurface)
            pygame.display.flip()

def runNovaGame():
    pygame.init()
    game = TitleScreen(width = 800, height = 800)
    game.play()

runNovaGame()