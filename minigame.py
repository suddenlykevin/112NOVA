#################################################
# NOVA TP2 Deliverable (Minigame)
#
# Your name: Kevin Xie
# Your andrew id: kevinx
#
#################################################

from algorithms import *
from classes import *
from main import *

class MiniGame(Mode):
    def __init__(self, control, screen, clock):
        super().__init__(control, screen, clock)
        self.gConstant = 6.7 * (10 ** -11)
        self.parcels = pygame.sprite.Group()
        self.planets = pygame.sprite.Group()
        self.customers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.growRate = 0.2
        self.mapSegments = [30, 30]
        self.currentPlanet = [None, False]
        self.map = generateMap(self.screen, self.planets, self.mapSegments)

    def returnToBase(self):
        pass

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
            elif self.control.options["path"] == "ColDiff" and done == False:
                if potential == None:
                    potential = ColDiffMap(self.screen, self.map,
                                           self.parcels).solve()
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
        for parcel in self.parcels:
            gravityAcceleration = pygame.math.Vector2(0, 0)
            for planet in self.planets:
                r = dist(parcel.pos, planet.pos)
                acceleration = (self.gConstant * planet.mass) / (r.magnitude())
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
        self.parcels = newParcels

    def growPlanet(self):
        if self.currentPlanet[1] == False:
            return
        else:
            pos = self.currentPlanet[0].pos
            r = self.currentPlanet[0].radius
            corners = [(pos[0] + r, pos[1] + r), (pos[0] - r, pos[1] + r),
                       (pos[0] - r, pos[1] - r), (pos[0] + r, pos[1] - r)]
            for corner in corners:
                if self.outOfBounds(corner):
                    return
            self.currentPlanet[0].update(self.growRate * self.clock.get_time())

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.enemies.add(Scavenger([0, 255, 0],
                                            pygame.mouse.get_pos()))
                elif event.key == pygame.K_q:
                    self.parcels = pygame.sprite.Group()
                    self.planets = pygame.sprite.Group()
                    self.customers = pygame.sprite.Group()
                    self.enemies = pygame.sprite.Group()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    self.currentPlanet = [Planet(self.screen,
                                                 pygame.mouse.get_pos()), True]
                    self.currentPlanet[0].update(0)
                    self.planets.add(self.currentPlanet[0])
                elif pygame.mouse.get_pressed()[2]:
                    self.parcels.add(
                        Parcel([0, 0, 255], pygame.mouse.get_pos(), "hello"))
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.currentPlanet[1]:
                    self.currentPlanet[1] = False
                    self.currentPlanet[0].mass = (2 * math.pi *
                                                  (self.currentPlanet[
                                                       0].radius ** 2) *
                                                  self.currentPlanet[0].density)
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def play(self):
        while self.running:
            self.screen.fill([0, 0, 0])
            self.checkCollisions()
            self.updateFollows()
            self.checkEvents()
            self.updatePhysics()
            self.growPlanet()
            self.planets.draw(self.screen)
            self.enemies.draw(self.screen)
            for parcel in self.parcels:
                if (parcel.trailPoints != None and len(set(parcel.trailPoints))
                        > 2):
                    pygame.draw.aalines(self.screen, [128] * 3, False,
                                        parcel.trailPoints)
            self.parcels.draw(self.screen)
            self.customers.draw(self.screen)
            self.clock.tick()
            pygame.display.flip()