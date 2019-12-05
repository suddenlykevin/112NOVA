#################################################
# NOVA TP2 Deliverable
#
# Your name: Kevin Xie
# Your andrew id: kevinx
#
# Asset Sources:
# Font : https://www.dafont.com/linear-beam.font
# Starman: http://joyreactor.cc/post/3862683
# Path: https://opengameart.org/content/16px-rounded-path-arrows
# Orb: https://opengameart.org/content/rotating-orbs
# Smoke: https://stock.adobe.com/images/pixel-art-explosion-game-icons-set-comic-boom-flame-effects-for-emotion/300428826
# Splash: https://66.media.tumblr.com/32fde74f7cde48f9235406b3ab634034/tumblr_p1uq4gd6Vn1u2j2n2o1_500.png
# Misc Sprites: https://stock.adobe.com/images/retro-space-arcade-game-invaders-spaceship-pixel-invader-monster-and-retro-video-games-pixel-art-isolated-objects-illustration-set/240215977
# Sonic: http://d-boome0811fmp.blogspot.com/2011/02/sonic-pixel.html
#
#################################################

import sys

from classes import *

from minigame import *

#################################################
#
# Helper Functions
#
#################################################

# matches sign of a given value to the determinant
def matchSign(value, determ):
    if determ < 0:
        return -1 * abs(value)
    return abs(value)

# CITATION: https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
# Almost Equal from 15-112 modified to allow a larger leeway
def almostEqual(x, y):
    return abs(x - y) < 1

# applies distance formula to two objects given cx and cy
def dist(object1, object2):
    r = pygame.math.Vector2(object2[0] - object1[0], object2[1] - object1[1])
    return r

# returns the key associated with the maximum value in a dict
def maxValKey(d):
    maxKey = None
    maxVal = 0
    for key in d:
        if not isinstance(d[key], str) and d[key] > maxVal:
            maxKey = key
            maxVal = d[key]
    return maxKey

#################################################
#
# Pygame "Mode" Classes
#
# CITATION: Loosely adapted from ModalApp:
# https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#subclassingModalApp
#
#################################################

# Mode superclass initializes all the default values
class Mode(object):
    def __init__(self, control, screen, clock):
        self.control = control
        self.running = True
        self.screen = screen
        self.clock = clock
        self.width, self.height = screen.get_width(), screen.get_height()

    def paused(self):
        pass

# Pauses game
class PauseScreen(Mode):
    def __init__(self, control, screen, clock):
        super().__init__(control, screen, clock)
        self.buttons = pygame.sprite.Group(Button(screen,
                                                  (self.width//10,
                                                   self.height//4),
                                                  (self.width//3,
                                                   self.height//16),
                                                  "Resume",
                                                  [128] * 3, self.returnTo),
                                           Button(screen,
                                                  (self.width // 10,
                                                   self.height // 3),
                                                  (self.width // 3,
                                                   self.height // 16),
                                                  "Options",
                                                  [128] * 3, self.options),
                                           RoundButton(
                                                      screen, (self.width//4,
                                                                self.height -
                                                                self.height//5),
                                                        50, "Menu",
                                                       [128] * 3, self.menu))

    # Return to menu (triggered by button)
    def menu(self):
        self.control.setActiveMode(self.control.splashMode)

    def toggleTrail(self):
        if self.control.options["trail"] == "ON":
            self.control.options["trail"] = "OFF"
        else:
            if self.control.options["gravity"] == "Field":
                self.control.options["trail"] = "ON"

    def toggleGravity(self):
        if self.control.options["gravity"] == "Field":
            self.control.options["gravity"] = "Nested"
            self.control.options["trail"] = "OFF"
        else:
            self.control.options["gravity"] = "Field"

    def togglePath(self):
        if self.control.options["path"] == "ColDiff":
            self.control.options["path"] = "Fast"
        else:
            self.control.options["path"] = "ColDiff"

    def options(self):
        toggle1 = Button(self.screen, (self.width * 6 // 10, self.height // 4),
                        (self.width // 3, self.height // 16),
                        f"{self.control.options['trail']}", [128] * 3,
                         self.toggleTrail)
        toggle2 = Button(self.screen, (self.width * 6 // 10, self.height // 3),
                        (self.width // 3, self.height // 16),
                        f"{self.control.options['gravity']}", [128] * 3,
                        self.toggleGravity)
        toggle3 = Button(self.screen, (self.width * 6 // 10, self.height * 5
                        // 12), (self.width // 3, self.height // 16),
                        f"{self.control.options['path']}", [128] * 3,
                        self.togglePath)
        optionButtons = pygame.sprite.Group(toggle1, toggle2, toggle3)
        while self.running:
            self.screen.fill([255, 255, 255])
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                elif event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
            font = pygame.font.Font('Linebeam.ttf', 20)
            labels = [font.render('Trails', True, [0] * 3), font.render(
                    'Gravity Calculation', True, [0] * 3),
                    font.render('Pathfinding', True, [0] * 3)]
            for i in range(len(labels)):
                surface = labels[i].get_rect()
                surface.topleft = (self.width // 10, self.height * 3 //
                                   12 + i * self.height // 12)
                self.screen.blit(labels[i], surface)
            optionButtons.update()
            toggle1.updateText(f"{self.control.options['trail']}")
            toggle2.updateText(f"{self.control.options['gravity']}")
            toggle3.updateText(f"{self.control.options['path']}")
            optionButtons.draw(self.screen)
            pygame.display.flip()

    def paused(self):
        self.buttons = pygame.sprite.Group(Button(self.screen,
                                                  (self.width // 10,
                                                   self.height // 4),
                                                  (self.width // 3,
                                                   self.height // 16),
                                                  "Resume",
                                                  [128] * 3, self.returnTo),
                                           Button(self.screen,
                                                  (self.width // 10,
                                                   self.height // 3),
                                                  (self.width // 3,
                                                   self.height // 16),
                                                  "Options",
                                                  [128] * 3, self.options),
                                           RoundButton(
                                               self.screen, (self.width // 4,
                                                        self.height -
                                                        self.height // 5),
                                               50, "Menu",
                                               [128] * 3, self.menu))

    def returnTo(self):
        self.control.setActiveMode(self.control.lastActive)

    # Main loop
    def play(self):
        while self.running:
            self.screen.fill([255,255,255])
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.returnTo()
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
    # Initial attributes
    def __init__(self, control, screen, clock, customMap = (False, None)):
        super().__init__(control, screen, clock)
        self.player = Player(self.screen, (self.width * 7 / 9, self.height * 7 /
                                           9))
        self.enemies = EnemyGroup()
        self.planets = pygame.sprite.Group()
        self.G = 6.7 * (10**-11)
        self.timer = 100
        self.growRate = 0.2
        if not customMap[0]:
            self.map = Map(self.screen, 4)
        else:
            self.map = customMap[1]
        self.currentPlanet = [None, False]
        self.wave = list(reversed(WaveGenerator(10, 15, 1).solve()))
        self.diff = 10
        self.length = 18
        self.maxDiff = 2
        self.waveNum = 1
        self.custom = customMap
        self.title = Title(self.screen, "Wave 1")
        self.shrinkRate = -0.005
        self.currentWall = [None, False]
        self.walls = pygame.sprite.Group()
        self.repair = False

    # updates global physics acting on each planet -- maybe create vector field?
    def updatePhysics(self):
        # nested loop may become inefficient
        for enemy in self.enemies:
            hit_list = pygame.sprite.spritecollide(enemy,self.map,False,
                                                   collided=pygame.sprite.collide_rect)
            for path in hit_list:
                if (self.map.spriteMap.index(path) != len(self.map.spriteMap)
                        - 1):
                    if path.direction[0] == 1:
                        if enemy.pos[0] < path.rect.center[0]:
                            r = path.rect.center
                        else:
                            r = self.map.spriteMap[
                                self.map.spriteMap.index(path) +
                                1].rect.center
                    elif path.direction[0] == -1:
                        if enemy.pos[0] < path.rect.center[0]:
                            r = self.map.spriteMap[
                                self.map.spriteMap.index(path) +
                                1].rect.center
                        else:
                            r = path.rect.center
                    elif path.direction[1] == 1:
                        if enemy.pos[1] < path.rect.center[1]:
                            r = path.rect.center
                        else:
                            r = self.map.spriteMap[
                                self.map.spriteMap.index(path) +
                                1].rect.center
                    elif path.direction[1] == -1:
                        if enemy.pos[1] < path.rect.center[1]:
                            r = self.map.spriteMap[
                                self.map.spriteMap.index(path) +
                                1].rect.center
                        else:
                            r = path.rect.center
                else:
                    r = self.player.rect.center
                theta = dist(enemy.pos, r).as_polar()[1]
                finalVelocity = pygame.math.Vector2()
                finalVelocity.from_polar((1, theta))
                finalVelocity *= enemy.pathSpeed
                enemy.pathVelocity = finalVelocity
        if len(self.enemies) > 0 and self.control.options["gravity"] == "Field":
            self.fieldPhysics()
        elif len(self.enemies) > 0 and self.control.options["gravity"] == "Nested":
            self.nestedPhysics()

    def nestedPhysics(self):
        gravityAcceleration = pygame.math.Vector2(0, 0)
        for enemy in self.enemies:
            hit_list = pygame.sprite.spritecollide(enemy, self.map, False,
                                                   collided=pygame.sprite.collide_rect)
            resist = False
            if len(hit_list) != 0:
                resist = True
            for planet in self.planets:
                r = dist(enemy.pos, planet.pos)
                acceleration = (self.G * planet.mass) / (r.magnitude())
                r.scale_to_length(acceleration)
                gravityAcceleration += r
            enemy.gravitate(gravityAcceleration, resist)

    def fieldPhysics(self):
        def f(planet, x, y):
            r = pygame.math.Vector2(planet.pos[0] - x, planet.pos[1] - y)
            g = 6.7 * (10**-8) * planet.mass / (r.as_polar()[0] ** 2)
            r.scale_to_length(g)
            return r
        def total(planets):
            if len(planets) > 0:
                def g(x, y):
                    gravSum = f(planets[0], x, y) + total(planets[1:])(x, y)
                    return gravSum
                return g
            else:
                def base(x, y):
                    return pygame.math.Vector2(0, 0)
                return base
        gravity = total(self.planets.sprites())
        for object in self.enemies:
            hit_list = pygame.sprite.spritecollide(object, self.map, False,
                                                   collided=pygame.sprite.collide_rect)
            resist = False
            if len(hit_list) != 0:
                resist = True
            accel = gravity(object.pos[0], object.pos[1])
            object.gravitate(accel, resist)

    # checks all "events" keystrokes, mousepresses etc.
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.control.setActiveMode(self.control.pauseMode)
                elif event.key == pygame.K_1:
                    self.enemies.add(Enemy(self.screen, (45, 45)))
                elif event.key == pygame.K_2:
                    self.enemies.add(EmptyEnemy(self.screen, (45, 45)))
                elif event.key == pygame.K_3:
                    self.enemies.add(ResistiveEnemy(self.screen, (45, 45)))
                elif event.key == pygame.K_4:
                    self.enemies.add(SpeedyEnemy(self.screen, (45, 45)))
                elif event.key == pygame.K_5:
                    self.enemies.add(DestructiveEnemy(self.screen, (45, 45)))
                elif event.key == pygame.K_RIGHT:
                    self.wave = []
                elif event.key == pygame.K_r:
                    if self.repair and self.player.repairFuel > 0:
                        self.player.repairFuel -= 1
                        self.control.miniGameMode = MiniGame(self.control,
                                                             self.screen,
                                                     self.clock, self.player)
                        if random.choice([True, False]):
                            self.player.pos = (random.uniform(0, self.width -
                                                              self.player.radius), 0)
                        else:
                            self.player.pos = (0, random.uniform(0, self.height - self.player.radius))
                        self.control.setActiveMode(self.control.miniGameMode)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if (not self.isInPlanet(pygame.mouse.get_pos()) and not
                            self.isInPath(pygame.mouse.get_pos())):
                        self.currentPlanet = [Planet(self.screen, pygame.mouse.get_pos()), True]
                        self.currentPlanet[0].update(0)
                        self.planets.add(self.currentPlanet[0])
                elif pygame.mouse.get_pressed()[2]:
                    if (not self.isInPlanet(pygame.mouse.get_pos()) and not
                            self.isInPath(pygame.mouse.get_pos()) and
                            self.player.fuel > 10 ** 3):
                        self.currentWall = [Wall(self.screen,
                                                   pygame.mouse.get_pos(),
                                                   None), True]
                        self.walls.add(self.currentWall[0])
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.currentPlanet[1]:
                    self.currentPlanet[1] = False
                    self.currentPlanet[0].mass = (2 * math.pi * 
                    (self.currentPlanet[0].radius**2) * self.currentPlanet[
                                                      0].density)
                elif self.currentWall[1]:
                    self.currentWall[1] = False
                    self.currentWall[0].pos1 = pygame.mouse.get_pos()
                    self.currentWall[0].mass = distance(
                        self.currentWall[0].pos0,
                        self.currentWall[0].pos1) * 10 ** 3
                    if self.player.fuel >= self.currentWall[0].mass:
                        self.player.fuel -= self.currentWall[0].mass
                    else:
                        self.currentWall[0].normalizeTo(self.player.fuel / (10
                                                                            ** 3))
                        self.player.fuel -= self.currentWall[0].mass
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
            if isinstance(enemy, DestructiveEnemy):
                hit_list = pygame.sprite.spritecollide(enemy, self.planets,
                                                       False,
                                           collided =
                                           pygame.sprite.collide_circle)
                hit_list[0].radius -= self.width//12
                if hit_list[0].radius < 2:
                    self.planets.remove(hit_list[0])
            self.player.fuel += enemy.mass * 4* 10 ** 3
            if self.player.fuel > 10 ** 6:
                self.player.fuel = 10 ** 6
        hit_list = pygame.sprite.spritecollide(self.player, self.enemies, True,
                                               collided =
                                               pygame.sprite.collide_circle)
        for enemy in hit_list:
            self.player.health -= 1
            if self.player.health == 0:
                self.control.endMode.status = 1
                self.control.endMode.score = self.waveNum
                self.control.setActiveMode(self.control.endMode)
        for enemy in self.enemies:
            if not (0 < enemy.pos[1] < self.height and 0 < enemy.pos[0] <
                    self.width):
                self.enemies.remove(enemy)

    def growPlanet(self):
        for planet in self.planets:
            if not (planet == self.currentPlanet[0] and self.currentPlanet[1]):
                planet.update(self.shrinkRate * self.clock.get_time())
                if planet.radius <= 2:
                     self.planets.remove(planet)
        if self.currentPlanet[1] == False:
            return
        collide = False
        for path in self.map:
            if (pygame.sprite.collide_circle(self.currentPlanet[0], path)):
                collide = True
        if (self.currentPlanet[0].pos[0] - self.currentPlanet[0].radius < 0 or
            self.currentPlanet[0].pos[0] + self.currentPlanet[0].radius > self.width or
            self.currentPlanet[0].pos[1] - self.currentPlanet[0].radius < 0 or
            self.currentPlanet[0].pos[1] + self.currentPlanet[0].radius > self.height):
            collide = True
        for planet in self.planets:
            if planet != self.currentPlanet[0] and pygame.sprite.collide_circle(
                planet, self.currentPlanet[0]):
                collide = True
        if (self.player.fuel > self.growRate and not collide and
                self.currentPlanet[0].radius < self.width//5):
            self.currentPlanet[0].update(self.growRate * self.clock.get_time())
            self.player.fuel -= self.growRate * self.currentPlanet[0].density\
                                / 2
        else:
            self.currentPlanet[1] = False

    def newMap(self):
        if self.custom[0]:
            self.map = self.custom[1]
        else:
            self.planets.empty()
            self.walls.empty()
            intricacy = 4
            if self.diff > 3:
                intricacy = 3
            elif self.diff > 6:
                intricacy = 2
            self.map = Map(self.screen, intricacy)

    def updateWave(self):
        if len(self.wave) > self.wave.count(0):
            if self.wave[-1] == 1:
                self.enemies.add(Enemy(self.screen, (45, 45)))
            elif self.wave[-1] == 2:
                self.enemies.add(EmptyEnemy(self.screen, (45, 45)))
            elif self.wave[-1] == 3:
                self.enemies.add(ResistiveEnemy(self.screen, (45, 45)))
            elif self.wave[-1] == 4:
                self.enemies.add(SpeedyEnemy(self.screen, (45, 45)))
            elif self.wave[-1] == 5:
                self.enemies.add(DestructiveEnemy(self.screen, (45,45)))
            self.wave.pop()
        elif len(self.enemies) == 0:
            diffDiff = 2
            lenDiff = 2
            if self.waveNum > 3:
                diffDiff = 5
                lenDiff = 4
            elif self.waveNum > 9 and self.diff < (self.length - 1) * 5:
                diffDiff = 1
                lenDiff = 0
            if self.waveNum <= 3:
                self.maxDiff = 2
            elif self.waveNum <= 5:
                self.maxDiff = 3
            elif self.waveNum <= 7:
                self.maxDiff = 4
            else:
                self.maxDiff = 5
            self.diff += diffDiff
            self.length += lenDiff
            self.wave = list(reversed(WaveGenerator(self.diff, self.length,
                                      self.maxDiff).solve()))
            self.newMap()
            self.waveNum += 1
            self.title = Title(self.screen, f"Wave {self.waveNum}")

    def play(self):
        timerFont = pygame.font.Font('Linebeam.ttf', 24)
        while self.running:
            self.screen.fill([0,0,0])
            self.checkEvents()
            self.checkCollisions()
            self.updatePhysics()
            self.growPlanet()
            self.timer -= self.clock.get_time() * 10**-3
            self.enemies.update(self.clock.get_time(), self.walls)
            self.map.draw(self.screen)
            self.planets.draw(self.screen)
            self.enemies.draw(self.screen)
            if self.currentWall[1]:
                if self.isInPath(pygame.mouse.get_pos()):
                    self.currentWall[1] = False
                    self.currentWall[0].pos1 = pygame.mouse.get_pos()
                    self.currentWall[0].mass = distance(
                        self.currentWall[0].pos0,
                        self.currentWall[0].pos1) * 10 ** 3
                    if self.player.fuel >= self.currentWall[0].mass:
                        self.player.fuel -= self.currentWall[0].mass
                    else:
                        self.currentWall[0].normalizeTo(self.player.fuel / (10
                                                        ** 3))
                        self.player.fuel -= self.currentWall[0].mass
                else:
                    self.currentWall[0].pos1 = pygame.mouse.get_pos()
            for wall in self.walls:
                wall.draw()
            timer = timerFont.render(f'{len(self.wave) - self.wave.count(0)}',
                                     True, [255] * 3)
            timerSurface = timer.get_rect()
            timerSurface.center = ((self.width//2, self.height*1//20))
            if not self.custom[0] and self.player.fuel <= (10 ** 6) / 3 or \
                self.player.health <= 5:
                self.repair = True
            else:
                self.repair = False
            if pygame.time.get_ticks() % 1000 == 0:
                self.updateWave()
            if self.title != None:
                self.screen.blit(self.title.image, self.title.rect)
                self.title.update()
                if self.title.tran <= 0:
                    self.title = None
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
        self.buttons = pygame.sprite.Group(
            RoundButton(screen,
                        [self.width // 5, self.height - self.height // 5],
                        50, "Play Again", [255, 0, 0], self.game),
            RoundButton(screen, [self.width - self.width // 5, self.height -
                                 self.height // 5], 50, "Menu", [255, 0, 0],
                        self.quit)
        )

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def quit(self):
        self.control.setActiveMode(self.control.splashMode)

    def game(self):
        self.control.gameMode = NovaGame(self.control, self.screen, self.clock)
        self.control.setActiveMode(self.control.gameMode)

    def paused(self):
        self.buttons = pygame.sprite.Group(
            RoundButton(self.screen,
                        [self.width // 5, self.height - self.height // 5],
                        50, "Play Again", [255, 0, 0], self.game),
            RoundButton(self.screen, [self.width - self.width // 5,
                                      self.height -
                                 self.height // 5], 50, "Exit", [255, 0, 0],
                        self.quit)
        )

    def play(self):
        while self.running:
            titleFont = pygame.font.Font('Linebeam.ttf', 48)
            littleFont = pygame.font.Font('Linebeam.ttf', 18)
            self.checkEvents()
            self.screen.fill([255, 255, 255])
            if self.status == 1:
                text = 'GAME OVER!'
            else:
                text = 'YAY DUMMY'
            titleText = titleFont.render(text, True, [
                (pygame.time.get_ticks() // 25) % 255] * 3)
            subTitle = littleFont.render(f'SCORE: {self.score}',
                                         True,
                                         [(pygame.time.get_ticks() // 25) % 255] * 3)
            textSurface = titleText.get_rect()
            subSurface = subTitle.get_rect()
            subSurface.center = ((self.width // 2, self.height * 3 // 5))
            textSurface.center = ((self.width // 2, self.height // 2))
            self.buttons.update()
            self.buttons.draw(self.screen)
            self.screen.blit(titleText, textSurface)
            self.screen.blit(subTitle, subSurface)
            pygame.display.flip()

# Title/splashscreen
class TitleScreen(Mode):
    def __init__(self, control, screen, clock):
        super().__init__(control, screen, clock)
        self.background = pygame.image.load('Assets/background.png')
        self.background = pygame.transform.scale(self.background,
                                                 (self.width, self.height))
        self.bgRect = self.background.get_rect()
        self.bgRect.topleft = (0, 0)
        self.player = Player(self.screen, (self.width//2 - self.width//16,
                                           self.height * 3 // 10))
        self.buttons = pygame.sprite.Group(
            Button(self.screen,
                   [self.width // 3, self.height + 10 - self.height * 4 //
                    20], [self.width // 3, self.height // 20], "Pathfinding "
                                                               "Demo",
                   [128, 128, 128], self.pathfinder),
            Button(self.screen,
                   [self.width // 3, self.height - self.height * 5 //
                    20], [self.width // 3, self.height // 20], "Level Editor",
                   [128, 128, 128], self.sandbox),
            RoundButton(self.screen,
                        [self.width // 5, self.height - self.height // 5],
                        50, "Play", [255, 0, 0], self.game),
            RoundButton(self.screen, [self.width - self.width // 5,
                                      self.height -
                                      self.height // 5], 50, "Exit",
                        [255, 0, 0],
                        self.quit))

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def quit(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def sandbox(self):
        self.control.sandBoxMode = SandBox(self.control, self.screen,
                                           self.clock)
        self.control.setActiveMode(self.control.sandBoxMode)

    def pathfinder(self):
        self.control.pathMode = PathMode(self.control, self.screen, self.clock)
        self.control.setActiveMode(self.control.pathMode)

    def game(self):
        self.control.gameMode = NovaGame(self.control, self.screen, self.clock)
        self.control.setActiveMode(self.control.gameMode)

    def paused(self):
        self.buttons = pygame.sprite.Group(
            Button(self.screen,
                   [self.width // 3, self.height + 10 - self.height * 4 //
                    20], [self.width // 3, self.height // 20],
                   "Pathfinding Demo",
                   [128, 128, 128], self.pathfinder),
            Button(self.screen,
                   [self.width // 3, self.height - self.height * 5 //
                    20], [self.width // 3, self.height // 20], "Level Editor",
                   [128, 128, 128], self.sandbox),
            RoundButton(self.screen,
                        [self.width // 5, self.height - self.height // 5],
                        50, "Play", [255, 0, 0], self.game),
            RoundButton(self.screen, [self.width - self.width // 5,
                                      self.height -
                                      self.height // 5], 50, "Exit",
                        [255, 0, 0],
                        self.quit))

    def play(self):
        titleFont = pygame.font.Font('Linebeam.ttf', 48)
        littleFont = pygame.font.Font('Linebeam.ttf', 18)
        while self.running:
            self.checkEvents()
            self.screen.blit(self.background, self.bgRect)
            titleText = titleFont.render('DON\'T TOUCH STARMAN', True,
                                         [(pygame.time.get_ticks(

            )//25) % 255] * 3)
            subTitle = littleFont.render('''PRESS AND HOLD TO ACTIVATE BUTTONS''', True, [(pygame.time.get_ticks()//25) % 255] * 3)
            textSurface = titleText.get_rect()
            subSurface = subTitle.get_rect()
            subSurface.center = ((self.width//2, self.height*3//5))
            textSurface.center = ((self.width//2, self.height//2))
            self.screen.blit(titleText, textSurface)
            self.screen.blit(subTitle, subSurface)
            self.player.draw()
            self.buttons.update()
            self.buttons.draw(self.screen)
            self.clock.tick()
            pygame.display.flip()

class ModeController(object):
    def __init__(self, width, height):
        self.clock = pygame.time.Clock()
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height))
        self.options = {"gravity": "Field", "path": "ColDiff", "trail": "ON"}
        pygame.display.set_caption('DON\'T TOUCH STARMAN')
        self.miniGameMode = None
        self.sandBoxMode = SandBox(self, self.screen, self.clock)
        self.pathMode = PathMode(self, self.screen, self.clock)
        self.pauseMode = PauseScreen(self, self.screen, self.clock)
        self.splashMode = TitleScreen(self, self.screen, self.clock)
        self.gameMode = NovaGame(self, self.screen, self.clock)
        self.endMode = EndScreen(self, self.screen, self.clock)
        self.activeMode = None
        self.lastActive = None
        self.setActiveMode(self.splashMode)

    def setActiveMode(self, mode):
        if self.activeMode == None:
            self.activeMode = mode
            self.activeMode.play()
        else:
            self.activeMode.running = False
            self.activeMode.paused()
            self.lastActive = self.activeMode
            self.activeMode = mode
            self.activeMode.running = True
            self.activeMode.play()

def runNovaGame():
    pygame.init()
    game = ModeController(width = 800, height = 800)

if __name__ == "__main__":
    runNovaGame()