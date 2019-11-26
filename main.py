#################################################
# NOVA TP1 Deliverable
#
# Your name: Kevin Xie
# Your andrew id: kevinx
#################################################

import sys

from classes import *

# matches sign of a given value to the determinant
def matchSign(value, determ):
    if determ < 0:
        return -1 * abs(value)
    return abs(value)

# https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
# modified to allow a larger leeway
def almostEqual(x, y):
    return abs(x - y) < 1

# applies distance formula to two objects given cx and cyrun
def dist(object1, object2):
    r = pygame.math.Vector2(object2[0] - object1[0], object2[1] - object1[1])
    return r

class Mode(object):
    def __init__(self, control, screen, clock):
        self.control = control
        self.running = True
        self.screen = screen
        self.clock = clock
        self.width, self.height = screen.get_width(), screen.get_height()

class PauseScreen(Mode):
    def __init__(self, control, screen, clock):
        super().__init__(control, screen, clock)
        self.buttons = pygame.sprite.Group(RoundButton(screen, (100, 100),
                                                        50, "Hello", [128] * 3))

    def play(self):
        while self.running:
            self.screen.fill([255,255,255])
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.control.setActiveMode(self.control.gameMode)
                elif event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
            self.buttons.update()
            self.buttons.draw(self.screen)
            self.clock.tick()
            pygame.display.flip()

# main gameplay
class NovaGame(Mode):
    def __init__(self, control, screen, clock):
        super().__init__(control, screen, clock)
        self.player = Player(self.screen, (self.width * 7 / 9, self.height * 7 /
                                           9))
        self.enemies = EnemyGroup()
        self.planets = pygame.sprite.Group()
        self.planetDensity = 10**4 # arbitrary value for now
        self.G = 6.7 * (10**-11)
        self.timer = 100
        self.growRate = 0.2
        self.map = Map(self.screen, 4)
        self.currentPlanet = [None, False]
        self.shrinkRate = -0.005

    # updates global physics acting on each planet -- maybe create vector field?
    def updatePhysics(self):
        # nested loop may become inefficient
        for enemy in self.enemies:
            finalVelocity = enemy.velocity
            hit_list = pygame.sprite.spritecollide(enemy,self.map,False,
                                                   collided=pygame.sprite.collide_rect)
            resist = False
            for path in hit_list:
                resist = True
                if not path.corner:
                    if path.direction[0] != 0:
                        finalVelocity[0] = path.direction[0]
                    else:
                        finalVelocity[1] = path.direction[1]
                elif finalVelocity.magnitude() < 0.15 and path.corner:
                    if path.direction[0] != 0:
                        if almostEqual(enemy.pos[1], path.pos[1] + path.size
                                                     / 2):
                            finalVelocity = pygame.math.Vector2(path.direction)
                        else:
                            diff = path.pos[1] + path.size / 2 - enemy.pos[1]
                            finalVelocity[1] = matchSign(path.direction[0],
                                                         diff)
                    else:
                        if almostEqual(enemy.pos[0], path.pos[0] + path.size
                                                     / 2):
                            finalVelocity = pygame.math.Vector2(path.direction)
                        else:
                            diff = path.pos[0] + path.size / 2 - enemy.pos[0]
                            finalVelocity[0] = matchSign(path.direction[1],
                                                         diff)
            gravityAcceleration = pygame.math.Vector2(0,0)
            for planet in self.planets:
                r = dist(enemy.pos, planet.pos)
                acceleration = (self.G * planet.mass) / (r.magnitude())
                r.scale_to_length(acceleration)
                gravityAcceleration += r
                if resist:
                    gravityAcceleration *= 0.3
            enemy.velocity = finalVelocity + gravityAcceleration

    # checks all "events" keystrokes, mousepresses etc.
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.control.setActiveMode(self.control.pauseMode)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if (not self.isInPlanet(pygame.mouse.get_pos()) and not
                            self.isInPath(pygame.mouse.get_pos())):
                        self.currentPlanet = [Planet(self.screen, pygame.mouse.get_pos()), True]
                        self.currentPlanet[0].update(0)
                        self.planets.add(self.currentPlanet[0])
                elif pygame.mouse.get_pressed()[2]:
                    self.enemies.add(Enemy(self.screen, pygame.mouse.get_pos()))
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.currentPlanet[1]:
                    self.currentPlanet[1] = False
                    self.currentPlanet[0].mass = (2 * math.pi * 
                    (self.currentPlanet[0].radius**2) * self.planetDensity)
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def isInPlanet(self, pos):
        for planet in self.planets:
            r = [planet.pos[0] - pos[0], planet.pos[1] - pos[1]]
            magnitude = (r[0]**2 + r[1]**2)**0.5
            if magnitude < planet.radius:
                self.currentPlanet = [planet, True]
                return True
        return False

    def isInPath(self, pos):
        for path in self.map:
            if (path.pos[0] < pos[0] < path.pos[0] + path.size and
                path.pos[1] < pos[1] < path.pos[1] + path.size):
                return True
        return False

    def checkCollisions(self):
        hit_list = []
        for planet in self.planets:
            hit_list += pygame.sprite.spritecollide(planet, self.enemies, True,
                                           collided =
                                           pygame.sprite.collide_circle)
        for enemy in hit_list:
            self.player.fuel += enemy.mass * 10 ** 4
            if self.player.fuel > 10 ** 6:
                self.player.fuel = 10 ** 6
        hit_list = pygame.sprite.spritecollide(self.player, self.enemies, True,
                                               collided =
                                               pygame.sprite.collide_circle)
        for enemy in hit_list:
            self.player.health -= 1
            if self.player.health == 0:
                self.control.endMode.status = 1
                self.control.endMode.score = self.player.score
                self.control.setActiveMode(self.control.endMode)

    def growPlanet(self):
        for planet in self.planets:
            if planet != self.currentPlanet[0] or not self.currentPlanet[1]:
                planet.update(self.shrinkRate * self.clock.get_time())
                if planet.radius <= 2:
                     self.planets.remove(planet)
        if self.currentPlanet[1] == False:
            return
        collide = False
        for path in self.map:
            if (pygame.sprite.collide_circle(self.currentPlanet[0], path)):
                collide = True
        if (self.player.fuel > self.growRate and not collide):
            self.currentPlanet[0].update(self.growRate * self.clock.get_time())
            self.player.fuel -= self.growRate * self.planetDensity / 2

    def play(self):
        timerFont = pygame.font.Font('Linebeam.ttf', 24)
        while self.running:
            self.screen.fill([0,0,0])
            self.checkEvents()
            self.checkCollisions()
            self.updatePhysics()
            self.growPlanet()
            self.timer -= self.clock.get_time() * 10**-3
            self.enemies.update(self.clock.get_time())
            self.map.draw(self.screen)
            self.planets.draw(self.screen)
            self.enemies.draw(self.screen)
            timer = timerFont.render(f'{int(self.timer)}', True, [255] * 3)
            timerSurface = timer.get_rect()
            timerSurface.center = ((self.width//2, self.height*1//20))
            self.screen.blit(timer, timerSurface)
            self.player.drawGUI()
            self.player.draw()
            self.clock.tick()
            pygame.display.flip()

class EndScreen(Mode):
    def __init__(self, control, screen, clock):
        super().__init__(control, screen, clock)
        self.status = 0
        self.score = 0

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.control.setActiveMode(self.control.gameMode)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.control.setActiveMode(self.control.gameMode)
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def play(self):
        while self.running:
            titleFont = pygame.font.Font('Linebeam.ttf', 48)
            littleFont = pygame.font.Font('Linebeam.ttf', 18)
            self.checkEvents()
            self.screen.fill([255, 255, 255])
            titleText = titleFont.render('NOVA', True, [
                (pygame.time.get_ticks() // 25) % 255] * 3)
            subTitle = littleFont.render('''PRESS ANYWHERE TO START GAME''',
                                         True,
                                         [(
                                                  pygame.time.get_ticks() // 25) % 255] * 3)
            textSurface = titleText.get_rect()
            subSurface = subTitle.get_rect()
            subSurface.center = ((self.width // 2, self.height * 3 // 5))
            textSurface.center = ((self.width // 2, self.height // 2))
            self.screen.blit(titleText, textSurface)
            self.screen.blit(subTitle, subSurface)
            pygame.display.flip()

# Title/splashscreen
class TitleScreen(Mode):
    def __init__(self, control, screen, clock):
        super().__init__(control, screen, clock)
        # self.buttons = pygame.sprite.Group(
        # RoundButton(),
        # RoundButton(),
        # RoundButton(),
        # RoundButton()
        # )
    
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.control.setActiveMode(self.control.gameMode)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.control.setActiveMode(self.control.gameMode)
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

class ModeController(object):
    def __init__(self, width, height):
        self.clock = pygame.time.Clock()
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('NOVA')
        self.splashMode = TitleScreen(self, self.screen, self.clock)
        self.gameMode = NovaGame(self, self.screen, self.clock)
        self.pauseMode = PauseScreen(self, self.screen, self.clock)
        self.endMode = EndScreen(self, self.screen, self.clock)
        self.setActiveMode(self.splashMode)

    def setActiveMode(self, mode):
        mode.play()

def runNovaGame():
    pygame.init()
    game = ModeController(width = 800, height = 800)

runNovaGame()