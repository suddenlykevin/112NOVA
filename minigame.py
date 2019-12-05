#################################################
# NOVA TP2 Deliverable (Minigame[s])
#
# Your name: Kevin Xie
# Your andrew id: kevinx
#
#################################################

from algorithms import *
from classes import *
from main import *

class MiniGame(Mode):
    def __init__(self, control, screen, clock, player):
        super().__init__(control, screen, clock)
        self.gConstant = 6.7 * (10 ** -11)
        self.mode = "fuel"
        self.modes = ["fuel", "health"]
        player.reserveFuel = (10 ** 6)
        self.player = player
        self.parcels = pygame.sprite.Group(self.newParcel())
        self.planets = pygame.sprite.Group()
        self.customers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group(Scavenger([255, 255, 255],
                                      (self.width / 2,
                                       self.height / 2)))
        self.growRate = 0.2
        self.mapSegments = [30, 30]
        self.currentPlanet = [None, False]
        self.shrinkPlanet = [None, False]
        self.map = generateMap(self.screen, self.planets, self.mapSegments)
        self.shrinkRate = -0.1
        self.active = False

    def newParcel(self):
        if self.player.pos[0] != 0:
            pos = (random.uniform(10, self.width - 10), self.height - 40)
            velocity = (0, -0.1)
        else:
            pos = (self.width - 10, random.uniform(10, self.height - 40))
            velocity = (-0.1, 0)
        return Parcel([255, 0, 0], pos, self.mode, velocity)

    def resetPlayer(self):
        if random.choice([True, False]):
            self.player.pos = (random.uniform(0, self.width -
                                              self.player.radius), 0)
        else:
            self.player.pos = (0, random.uniform(0, self.height -
                                                 self.player.radius - 30))

    def returnToBase(self):
        for enemy in self.enemies:
            if abs(self.width/2 - enemy.pos[0]) < 25 and abs(self.height/2 -
                                                        enemy.pos[1]) < 25:
                return
        self.map = generateMap(self.screen, self.planets, self.mapSegments)
        if (self.control.options["path"] in ["ColDiff", "Fast"]):
            if self.control.options["path"] == "Fast":
                potential = ColDiffMap(self.screen, self.map,
                                       [Parcel([0] * 3, (self.width/2,
                                                         self.height/2),
                                               "health",
                                               (0,0))],
                                       self.enemies).solve()
            else:
                potential = ColDiffMap(self.screen, self.map,
                                       [Parcel([0] * 3, (self.width/2,
                                                         self.height/2),
                                               "health",
                                               (0,0))],
                                       self.enemies,
                                       False).solve()
        directions = {(-1, -1): -135,
                      (0, -1): -90,
                      (1, -1): -45,
                      (-1, 0): -180,
                      (1, 0): 0,
                      (-1, 1): 135,
                      (0, 1): 90,
                      (1, 1): 45}
        for enemy in self.enemies:
            pos = self.viewToModel(enemy.pos)
            choices = {}
            for d in directions:
                if (0 <= pos[1] + d[1] < len(potential)
                        and 0 <= pos[0] + d[0] < len(potential[0])):
                    choices[d] = potential[pos[1] + d[1]][pos[0] + d[0]]
            best = maxValKey(choices)
            if best == None:
                best = 0
            else:
                best = directions[best]
            enemy.velocity.from_polar((enemy.velocity.length(), best))
            enemy.move(self.clock.get_time())

    def updateFollows(self):
        self.map = generateMap(self.screen, self.planets, self.mapSegments)
        potential = None
        directions = {(-1, -1): -135,
                      (0, -1): -90,
                      (1, -1): -45,
                      (-1, 0): -180,
                      (1, 0): 0,
                      (-1, 1): 135,
                      (0, 1): 90,
                      (1, 1): 45}
        if len(self.parcels) == 0:
            self.returnToBase()
            return
        for enemy in self.enemies:
            done = False
            for parcel in self.parcels:
                if self.crowFlies(parcel.pos, enemy.pos):
                    theta = dist(enemy.pos, parcel.pos).as_polar()[1]
                    enemy.velocity.from_polar((enemy.velocity.length(), theta))
                    done = True
            if self.control.options["path"] == "AStar" and done == False:
                target = random.choice(self.parcels.sprites())
                best = AStarMap(self.screen, self.map, enemy.pos,
                                target.pos).solve()
                enemy.velocity.from_polar((enemy.velocity.length(), best))
            elif (self.control.options["path"] in ["ColDiff", "Fast"] and done
                    == False):
                if potential == None and self.control.options["path"] == "Fast":
                    potential = ColDiffMap(self.screen, self.map,
                                           self.parcels, self.enemies).solve()
                elif potential == None:
                    potential = ColDiffMap(self.screen, self.map,
                                           self.parcels, self.enemies,
                                           False).solve()
                pos = self.viewToModel(enemy.pos)
                choices = {}
                for d in directions:
                    if (0 <= pos[1] + d[1] < len(potential)
                            and 0 <= pos[0] + d[0] < len(potential[0])):
                        choices[d] = potential[pos[1] + d[1]][pos[0] + d[0]]
                best = maxValKey(choices)
                if best == None:
                    best = 0
                else:
                    best = directions[best]
                enemy.velocity.from_polar((enemy.velocity.length(), best))
            enemy.move(self.clock.get_time())

    def viewToModel(self, tuple):
        dX = self.width / len(self.map[1])
        dY = self.height / len(self.map[0])
        result = (round(tuple[0] / dX), round(tuple[1] / dY))
        return result

    def crowFlies(self, pos0, pos1):
        def f(x):
            g = (pos1[1] - pos0[1]) / (pos1[0] - pos0[0])
            return g * (x - pos0[0]) + pos0[1]

        pos0 = self.viewToModel(pos0)
        pos1 = self.viewToModel(pos1)
        for x in range(min(pos0[0], pos1[0]), max(pos0[0], pos1[0]) + 1):
            for y in range(min(pos0[1], pos1[1]), max(pos0[1], pos1[1]) + 1):
                if (0 <= x < self.mapSegments[0] and 0 <= y < self.mapSegments[
                    1]) and self.map[y][x] == "@":
                    return False
        return True

    def updatePhysics(self):
        if self.control.options["gravity"] == "Field":
            self.fieldPhysics()
        elif self.control.options["gravity"] == "Nested":
            self.nestedPhysics()

    def nestedPhysics(self):
        if self.active:
            for parcel in self.parcels:
                gravityAcceleration = pygame.math.Vector2(0, 0)
                for planet in self.planets:
                    r = dist(parcel.pos, planet.pos)
                    acceleration = (self.gConstant * planet.mass) / (r.magnitude()**2)
                    r.scale_to_length(acceleration)
                    gravityAcceleration += r
                parcel.velocity += gravityAcceleration
                parcel.move(self.clock.get_time())

    def fieldPhysics(self):
        def f(planet, x, y):
            r = pygame.math.Vector2(planet.pos[0] - x, planet.pos[1] - y)
            g = self.gConstant * planet.mass / (r.as_polar()[0] ** 2)
            r.scale_to_length(g)
            return r
        def total(planets):
            if len(planets) > 0:
                def g(pos):
                    (x, y) = pos
                    gravSum = f(planets[0], x, y) + total(planets[1:])(pos)
                    return gravSum

                return g
            else:
                def base(pos):
                    return pygame.math.Vector2(0, 0)
                return base
        gravity = total(self.planets.sprites())
        for parcel in self.parcels:
            if self.active:
                parcel.velocity += gravity(parcel.pos)
                parcel.move(self.clock.get_time())
            if self.control.options["trail"] == "ON":
                linePoints = [parcel.pos]
                velocity = copy.copy(parcel.velocity)
                while (not (self.outOfBounds(linePoints[-1])
                            or self.inPlanet(linePoints[-1])) and
                       len(linePoints) < 25000):
                    velocity += gravity(linePoints[-1])
                    linePoints += [(linePoints[-1][0] + velocity.x *
                                    self.clock.get_time(),
                                    linePoints[-1][1] + velocity.y *
                                    self.clock.get_time())]
                parcel.trailPoints = linePoints

    def inPlanet(self, pos):
        for planet in self.planets:
            if planet.rect.collidepoint(pos):
                return True
        return False

    def outOfBounds(self, pos):
        x, y = pos[0], pos[1]
        return not (0 <= x < self.width and 0 <= y < self.height)

    def checkCollisions(self):
        hit_list = []
        for planet in self.planets:
            hit_list += pygame.sprite.spritecollide(planet, self.parcels, True,
                                                    collided=
                                                    pygame.sprite.collide_circle)
        hit_list = []
        newEnemies = self.enemies.copy()
        for enemy in self.enemies:
            hit_list += pygame.sprite.spritecollide(enemy, self.parcels, True,
                                                    collided=
                                                    pygame.sprite.collide_circle)
            if self.outOfBounds(enemy.pos):
                newEnemies.remove(enemy)
        self.enemies = newEnemies
        newParcels = self.parcels.copy()
        for parcel in self.parcels:
            if self.outOfBounds(parcel.pos):
                newParcels.remove(parcel)
            if pygame.sprite.collide_circle(parcel, self.player):
                newParcels.remove(parcel)
                if parcel.key == "fuel":
                    self.player.fuel += (10 ** 6) / 5
                    if self.player.fuel > 10 ** 6:
                        self.player.fuel = 10 ** 6
                elif parcel.key == "health":
                    self.player.health += 1
                    if self.player.health > 10:
                        self.player.health = 10
        self.parcels = newParcels

    def growPlanet(self):
        if self.currentPlanet[1] == False:
            return
        collide = False
        if (self.currentPlanet[0].pos[0] - self.currentPlanet[0].radius < 0 or
            self.currentPlanet[0].pos[0] + self.currentPlanet[0].radius > self.width or
            self.currentPlanet[0].pos[1] - self.currentPlanet[0].radius < 0 or
            self.currentPlanet[0].pos[1] + self.currentPlanet[0].radius > self.height):
            collide = True
        if pygame.sprite.collide_circle(self.enemies.sprites()[0],
                                        self.currentPlanet[0]):
            collide = True
        for planet in self.planets:
            if planet != self.currentPlanet[0] and pygame.sprite.collide_circle(
                planet, self.currentPlanet[0]):
                collide = True
        if (self.player.reserveFuel > self.growRate and not collide and
                self.currentPlanet[0].radius < self.width//6):
            self.currentPlanet[0].update(self.growRate * self.clock.get_time())
            self.player.reserveFuel -= self.growRate * self.currentPlanet[
                0].density/ 10 ** 2
        else:
            self.currentPlanet[1] = False

    def isInPlanet(self, pos):
        for planet in self.planets:
            r = [planet.pos[0] - pos[0], planet.pos[1] - pos[1]]
            magnitude = (r[0]**2 + r[1]**2)**0.5
            if magnitude < planet.radius:
                self.currentPlanet = [planet, True]
                return True
        return False

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.control.setActiveMode(self.control.pauseMode)
                elif event.key == pygame.K_SPACE:
                    self.active = True
                elif event.key == pygame.K_q:
                    self.parcels = pygame.sprite.Group()
                    self.planets = pygame.sprite.Group()
                    self.customers = pygame.sprite.Group()
                    self.enemies = pygame.sprite.Group()
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    self.mode = self.modes[(self.modes.index(self.mode) + 1)
                                           % len(self.modes)]
                    self.parcels.sprites()[0].key = self.mode
                    self.parcels.sprites()[0].update()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if (not self.isInPlanet(pygame.mouse.get_pos()) and
                            self.player.reserveFuel > 10 ** 3):
                        self.currentPlanet = [Planet(self.screen, pygame.mouse.get_pos()), True]
                        self.currentPlanet[0].density = 10 ** 7
                        self.currentPlanet[0].update(0)
                        self.planets.add(self.currentPlanet[0])
                elif pygame.mouse.get_pressed()[2]:
                    for planet in self.planets:
                        if planet.rect.collidepoint(pygame.mouse.get_pos()):
                            self.shrinkPlanet = [planet, True]
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.currentPlanet[1]:
                    self.currentPlanet[1] = False
                    self.currentPlanet[0].mass = (2 * math.pi *
                                                  (self.currentPlanet[
                                                       0].radius ** 2) *
                                                  self.currentPlanet[0].density)
                if self.shrinkPlanet[1]:
                    self.shrinkPlanet[1] = False
                    self.currentPlanet[0].mass = (2 * math.pi *
                                                  (self.currentPlanet[
                                                       0].radius ** 2) *
                                                  self.currentPlanet[0].density)
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def shrink(self):
        self.player.reserveFuel -= self.shrinkRate * 10 ** 3 * \
                                   self.clock.get_time() / 2
        self.shrinkPlanet[0].update(self.shrinkRate * self.clock.get_time())
        if self.shrinkPlanet[0].radius <= 2:
            self.planets.remove(self.shrinkPlanet[0])
            self.shrinkPlanet[1] = False
            self.player.reserveFuel += self.shrinkRate * 2 * 10 ** 3 * \
                                      self.clock.get_time() / 2

    def returnToGame(self):
        self.player.pos = (self.width * 7 / 9, self.height * 7 /
                           9)
        self.control.setActiveMode(self.control.gameMode)

    def play(self):
        while self.running:
            self.screen.fill([0, 0, 0])
            self.checkCollisions()
            if self.active:
                self.updateFollows()
            else:
                self.returnToBase()
            self.checkEvents()
            self.updatePhysics()
            self.growPlanet()
            if self.shrinkPlanet[1]:
                self.shrink()
            self.planets.draw(self.screen)
            self.enemies.draw(self.screen)
            for parcel in self.parcels:
                if (parcel.trailPoints != None and len(set(parcel.trailPoints))
                        > 2 and self.control.options["trail"] == "ON"):
                    pygame.draw.aalines(self.screen, [128] * 3, False,
                                        parcel.trailPoints)
            self.parcels.draw(self.screen)
            self.customers.draw(self.screen)
            self.player.draw()
            self.player.drawGUI(reserve = True)
            if self.player.health == 10 and self.player.fuel == 10 ** 6:
                self.returnToGame()
            if len(self.parcels) == 0:
                if self.player.reserveFuel < 10 ** 3 and len(self.planets) == 0:
                    self.returnToGame()
                self.resetPlayer()
                self.parcels.add(self.newParcel())
                self.active = False
            self.clock.tick(25)
            pygame.display.flip()

class SandBox(Mode):
    def __init__(self, control, screen, clock):
        super().__init__(control, screen, clock)
        self.map = MapGenerator(8, 8, 1, (7, 7))
        self.player = Player(self.screen, (self.width * 7 / 9, self.height * 7 /
                                           9))
        self.playButton = pygame.sprite.Group(
            RoundButton(self.screen, (self.width * 7 / 9 + self.width/16,
                        self.height * 7 / 9 + self.width/16), self.width/16,
                        "PLAY", [0, 0, 255], self.playMap)
        )
        self.coords = [(0, 0)]
        self.validity = True
        self.complete = False

    def playMap(self):
        map = Map(self.screen, None, (False, self.coords))
        mode = NovaGame(self.control, self.screen, self.clock, (True, map))
        self.control.setActiveMode(mode)

    def viewToModel(self, tuple):
        dX = self.width // 9
        dY = self.height // 9
        result = (tuple[0] // dX, tuple[1] // dY)
        if result[0] > 8 or result[1] > 8:
            return None
        return result

    def modelToView(self, tuple):
        dX = self.width // 9
        dY = self.height // 9
        result = (tuple[0] * dX, tuple[1] * dY)
        return result

    def toggle(self, tuple):
        if tuple == (0, 0):
            return
        if tuple in self.coords:
            self.coords.remove(tuple)
        else:
            self.coords.append(tuple)

    def organizeCoords(self):
        organized = [(0, 0)]
        coords = self.coords[1:]
        while len(coords) > 0:
            pos = organized[-1]
            if ((pos[0], pos[1] + 1) in coords):
                organized.append((pos[0], pos[1] + 1))
                coords.remove((pos[0], pos[1] + 1))
            elif (pos[1] > 0 and (pos[0], pos[1] - 1) in coords):
                organized.append((pos[0], pos[1] - 1))
                coords.remove((pos[0], pos[1] - 1))
            elif (pos[0] + 1, pos[1]) in coords:
                organized.append((pos[0] + 1, pos[1]))
                coords.remove((pos[0] + 1, pos[1]))
            elif (pos[0] > 0 and (pos[0] - 1, pos[1]) in coords):
                organized.append((pos[0] - 1, pos[1]))
                coords.remove((pos[0] - 1, pos[1]))
            else:
                return False
            if len(set(organized)) != len(organized):
                return False
        self.coords = organized
        return True

    def checkValidity(self):
        if not self.organizeCoords():
            self.validity = False
            self.complete = False
            return
        state = MapState(self.coords)
        if self.map.stateSatisfiesConstraints(state):
            self.validity = True
        else:
            self.validity = False
        if self.map.isSolutionState(state):
            self.complete = True
        else:
            self.complete = False

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.control.setActiveMode(self.control.pauseMode)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    pos = self.viewToModel(pygame.mouse.get_pos())
                    if self.complete and pos == (7, 7):
                        continue
                    if pos != None:
                        self.toggle(pos)
                    self.checkValidity()
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def play(self):
        while self.running:
            self.screen.fill([0, 0, 0])
            self.checkEvents()
            if self.complete:
                color = [0, 255, 0]
            elif not self.validity:
                color = [255, 0, 0]
            else:
                color = [32, 32, 64]
            for coord in self.coords:
                pos = self.modelToView(coord)
                size = self.width//9
                rect = pygame.Rect(pos[0], pos[1], size, size)
                pygame.draw.rect(self.screen, color, rect)
            self.player.draw()
            if self.complete:
                self.playButton.update()
                self.playButton.draw(self.screen)
            self.clock.tick()
            pygame.display.flip()

class PathMode(Mode):
    def __init__(self, control, screen, clock):
        super().__init__(control, screen, clock)
        self.blots = pygame.sprite.Group()
        self.targets = pygame.sprite.Group(Parcel([0, 255, 0],
                                                  (self.width/2,
                                                  self.height/2), "health",
                                                  (0,0)))
        self.enemies = pygame.sprite.Group(Scavenger([255,255,255],
                                                     (self.width/2,
                                                      10)))
        self.dragging = [False, None]
        self.mapSegments = [30, 30]
        self.active = False

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pygame.mouse.get_pressed()[0]:
                    for target in self.targets:
                        if target.rect.collidepoint(pos):
                            self.dragging = [True, target]
                    for enemy in self.enemies:
                        if enemy.rect.collidepoint(pos):
                            self.dragging = [True, enemy]
                    if not self.dragging[0]:
                        self.blots.add(Blot(pos))
                elif pygame.mouse.get_pressed()[2]:
                    self.targets.add(Parcel([0, 255, 0], pos, "health",
                                            (0,0)))
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging[0]:
                    self.dragging[0] = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.control.setActiveMode(self.control.pauseMode)
                elif event.key == pygame.K_q:
                    self.targets = pygame.sprite.Group()
                    self.blots = pygame.sprite.Group()
                    self.enemies = pygame.sprite.Group()
                elif event.key == pygame.K_SPACE:
                    self.active = not self.active
                elif event.key == pygame.K_r:
                   self.enemies.add(Scavenger([255, 255, 255],
                                              pygame.mouse.get_pos()))
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def viewToModel(self, tuple):
        dX = self.width / len(self.map[1])
        dY = self.height / len(self.map[0])
        result = (round(tuple[0] / dX), round(tuple[1] / dY))
        return result

    def crowFlies(self, pos0, pos1):
        def f(x):
            g = (pos1[1] - pos0[1]) / (pos1[0] - pos0[0])
            return g * (x - pos0[0]) + pos0[1]
        pos0 = self.viewToModel(pos0)
        pos1 = self.viewToModel(pos1)
        for x in range(min(pos0[0],pos1[0]), max(pos0[0],pos1[0]) + 1):
            for y in range(min(pos0[1],pos1[1]), max(pos0[1],pos1[1]) + 1):
                if (0 <= x < self.mapSegments[0] and 0 <= y < self.mapSegments[
                    1]) and self.map[y][x] == "@":
                    return False
        return True

    def updateFollows(self):
        self.map = generateMap(self.screen, self.blots, self.mapSegments)
        potential = None
        directions = {(-1, -1): -135,
                      (0, -1): -90,
                      (1, -1): -45,
                      (-1, 0): -180,
                      (1, 0): 0,
                      (-1, 1): 135,
                      (0, 1): 90,
                      (1, 1): 45}
        for enemy in self.enemies:
            done = False
            for parcel in self.targets:
                if self.crowFlies(parcel.pos, enemy.pos):
                    theta = dist(enemy.pos, parcel.pos).as_polar()[1]
                    enemy.velocity.from_polar((enemy.velocity.length(), theta))
                    done = True
            if self.control.options["path"] == "AStar" and done == False:
                target = random.choice(self.targets.sprites())
                best = AStarMap(self.screen, self.map, enemy.pos,
                                target.pos).solve()
                enemy.velocity.from_polar((enemy.velocity.length(), best))
            elif (self.control.options["path"] in ["ColDiff", "Fast"] and done
                  == False):
                if potential == None and self.control.options["path"] == "Fast":
                    potential = ColDiffMap(self.screen, self.map,
                                           self.targets, self.enemies).solve()
                elif potential == None:
                    potential = ColDiffMap(self.screen, self.map,
                                           self.targets, self.enemies,
                                           False).solve()
                pos = self.viewToModel(enemy.pos)
                choices = {}
                for d in directions:
                    if (0 <= pos[1] + d[1] < len(potential)
                            and 0 <= pos[0] + d[0] < len(potential[0])):
                        choices[d] = potential[pos[1] + d[1]][pos[0] + d[0]]
                best = maxValKey(choices)
                if best == None:
                    best = 0
                else:
                    best = directions[best]
                enemy.velocity.from_polar((enemy.velocity.length(), best))
            enemy.move(self.clock.get_time())

    def checkCollisions(self):
        hit_list = []
        newEnemies = self.enemies.copy()
        for enemy in self.enemies:
            hit_list += pygame.sprite.spritecollide(enemy, self.targets, True,
                                                    collided =
                                                    pygame.sprite.collide_circle)

    def play(self):
        while self.running:
            self.screen.fill([0, 0, 0])
            if self.active and len(self.targets) > 0:
                self.updateFollows()
            self.checkEvents()
            self.checkCollisions()
            if self.dragging[0]:
                self.dragging[1].pos = pygame.mouse.get_pos()
                self.dragging[1].update()
            self.blots.draw(self.screen)
            self.enemies.draw(self.screen)
            self.targets.draw(self.screen)
            self.clock.tick()
            pygame.display.flip()