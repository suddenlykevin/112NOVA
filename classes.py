#################################################
# NOVA TP2 Deliverable (Classes)
#
# Your name: Kevin Xie
# Your andrew id: kevinx
#################################################

import math

import pygame

from algorithms import *

def distance(pos0, pos1):
    x = pos0[0] - pos1[0]
    y = pos0[1] - pos1[1]
    return (x**2 + y**2)**0.5

# holds player position and attributes
class Player(pygame.sprite.Sprite):
    def __init__(self, screen, pos):
        super().__init__()
        self.screen = screen
        self.pos = pos
        self.score = 0
        self.fuel = 10 ** 6
        self.reserveFuel = (10 ** 6)
        self.repairFuel = 3
        self.health = 8
        self.spriteList = self.retrieveSprites()
        self.spriteFrames = [0, 0]
        self.radius = self.screen.get_width()//16
        self.image = self.spriteList[0]
        self.image = pygame.transform.scale(self.image, (self.radius * 2,) * 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

    def drawGUI(self, reserve = False):
        ratio = self.fuel / 10 ** 6
        fuelBar = pygame.Rect(0, self.screen.get_height() - 10,
                              self.screen.get_width() * ratio, 10)
        pygame.draw.rect(self.screen, [255, 127, 0], fuelBar)
        healthRatio = self.health / 8
        healthBar = pygame.Rect(0, self.screen.get_height() - 20,
                                self.screen.get_width() * healthRatio, 10)
        pygame.draw.rect(self.screen, [255, 0, 32], healthBar)
        if reserve == True:
            reserveRatio = self.reserveFuel / ((10 ** 6))
            reserveBar = pygame.Rect(0, self.screen.get_height() - 30,
                                    self.screen.get_width() * reserveRatio, 10)
            pygame.draw.rect(self.screen, [0, 255, 0], reserveBar)
        elif self.health <= 2 or self.fuel <= (10 ** 6) / 4:
            self.font = pygame.font.Font('Linebeam.ttf', 18)
            rPrompt = pygame.Surface((15,30))
            rPrompt.fill([255, 127, 0])
            rect = rPrompt.get_rect()
            rect.bottomleft = (15, self.screen.get_height() - 25)
            textSurf = self.font.render(f"{self.repairFuel}", True, [255, 255,
                                                                  255])
            textRect = textSurf.get_rect()
            textRect.center = ((7.5, 15))
            rPrompt.blit(textSurf, textRect)
            self.screen.blit(rPrompt, rect)

    def draw(self):
        self.spriteFrames[1] += 1
        if self.spriteFrames[1] >= 1000:
            self.spriteFrames[1] = 0
            self.spriteFrames[0] = (self.spriteFrames[0] + 1) % 4
            self.image = self.spriteList[self.spriteFrames[0]]
        self.radius = self.screen.get_width() // 16
        self.image = pygame.transform.scale(self.image, (self.radius * 2,) * 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.screen.blit(self.image,self.rect)

    def retrieveSprites(self):
        spriteLoc = ["Assets/player1.png", "Assets/player2.png",
                   "Assets/player3.png", "Assets/player4.png"]
        sprites = []
        for path in spriteLoc:
            sprites.append(pygame.image.load(path).convert_alpha())
        return sprites

class Planet(pygame.sprite.Sprite):
    def __init__(self, screen, pos):
        super().__init__()
        self.screen = screen
        self.pos = pos
        self.density = 7 * 10 ** 3
        self.radius = 0
        self.mass = 0

    def retrieveSprites(self):
        pass

    def update(self, rate):
        self.radius += rate
        if rate < 0 and self.radius <= 2:
            return
        self.mass = math.pi * (self.radius ** 2) * self.density
        self.image = pygame.Surface([self.radius * 2, self.radius * 2],
                                    pygame.SRCALPHA)
        self.image.fill([255,255,255, 0])
        pygame.draw.circle(self.image, [255, 0, 0], (self.radius, self.radius),
                           self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

# pass in cx, cy
class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen, pos):
        super().__init__()
        self.screen = screen
        self.pos = pos
        self.pathSpeed = random.uniform(0.075, 0.15)
        self.velocity = pygame.math.Vector2(0,0)
        self.pathVelocity = pygame.math.Vector2(0,0)
        self.mass = 10
        self.radius = 10
        self.damage = 1
        self.gravityMult = 1
        self.gravityAcc = pygame.math.Vector2(0,0)
        self.image = pygame.image.load('Assets/normal.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.resist = False

    def move(self, time):
        if not self.resist:
            mult = 0
        else:
            mult = 1
        self.velocity = self.pathVelocity * mult + self.gravityAcc * self.gravityMult
        self.pos = tuple((self.pos[i] + self.velocity[i] * time) for i in range(
            len(self.velocity)))
        self.updateSprite()
        self.rect.center = self.pos

    def updateSprite(self):
        self.image = pygame.image.load('Assets/normal.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.image = pygame.transform.rotate(self.image,
                                             -self.velocity.as_polar()[1])

    def gravitate(self, vector, resist):
        # If gravity = 0, gravity acceleration = 0
        if vector.length() == 0 :
            self.gravityAcc = pygame.math.Vector2(0,0)
        # if in path, resist
        if resist:
            self.resist = True
            self.gravityAcc += vector * 0.3 * resist
        elif self.resist:
            self.resist = False
            self.gravityAcc = vector
        else:
            self.gravityAcc += vector

class PathPiece(pygame.sprite.Sprite):
    directions = [[1,0], [0,1], [-1,0], [0,-1]]
    def __init__(self, pos, size, orientation, corner):
        super().__init__()
        self.orientation = orientation
        self.corner = corner
        self.size = size
        self.sprites = ['Assets/horizontal.png', 'Assets/vertical.png']
        self.corners = ['Assets/corner1.png', 'Assets/corner2.png',
                        'Assets/corner3.png', 'Assets/corner4.png']
        if corner[0]:
            self.image = pygame.image.load(self.corners[corner[1]]).convert_alpha()
        else:
            self.image = pygame.image.load(self.sprites[
                                           orientation % 2]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.direction = PathPiece.directions[orientation]

class Map(pygame.sprite.Group):
    def __init__(self, screen, diff, autoGenerate = (True, None)):
        if autoGenerate[0] == True:
            self.coords = MapGenerator(8, 8, diff, (7, 7)).solve()
        else:
            self.coords = autoGenerate[1]
        self.screen = screen
        self.tileSize = self.screen.get_width() // 9
        self.spriteMap = self.retrieveSprites()
        super().__init__(self.spriteMap)

    def retrieveSprites(self):
        spriteList = []
        for i in range(len(self.coords)):
            if i < len(self.coords) - 1:
                if self.coords[i][0] < self.coords[i+1][0]:
                    orientation = 0
                elif self.coords[i][0] > self.coords[i+1][0]:
                    orientation = 2
                elif self.coords[i][1] < self.coords[i+1][1]:
                    orientation = 1
                else:
                    orientation = 3
            corner = (False, None)
            if i > 0:
                if (spriteList[-1].orientation == 0 and orientation == 1 or
                    spriteList[-1].orientation == 3 and orientation == 2):
                    corner = (True, 2)
                elif (spriteList[-1].orientation == 2 and orientation == 1 or
                      spriteList[-1].orientation == 3 and orientation == 0):
                    corner = (True, 3)
                elif (spriteList[-1].orientation == 0 and orientation == 3 or
                      spriteList[-1].orientation == 1 and orientation == 2):
                    corner = (True, 1)
                elif (spriteList[-1].orientation == 2 and orientation == 3 or
                      spriteList[-1].orientation == 1 and orientation == 0):
                    corner = (True, 0)
            transCoord = [elem * self.tileSize for elem in self.coords[i]]
            spriteList.append(PathPiece(transCoord, self.tileSize, orientation,
                                     corner))
        return spriteList

# test subclass of enemy
class DestructiveEnemy(Enemy):
    def __init__(self, screen, pos):
        super().__init__(screen, pos)
        self.mass = 0
        self.image = pygame.image.load('Assets/bomb.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def updateSprite(self):
        self.image = pygame.image.load('Assets/bomb.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.image = pygame.transform.rotate(self.image,
                                             -self.velocity.as_polar()[1])

class EmptyEnemy(Enemy):
    def __init__(self, screen, pos):
        super().__init__(screen, pos)
        self.mass = 0
        self.radius = 10
        self.image = pygame.image.load('Assets/bubble.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def updateSprite(self):
        self.image = pygame.image.load('Assets/bubble.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.image = pygame.transform.rotate(self.image,
                                             -self.velocity.as_polar()[1])

class ResistiveEnemy(Enemy):
    def __init__(self, screen, pos):
        super().__init__(screen, pos)
        self.gravityMult = 0.6
        self.image = pygame.image.load('Assets/heavy.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def updateSprite(self):
        self.image = pygame.image.load('Assets/heavy.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.image = pygame.transform.rotate(self.image,
                                             -self.velocity.as_polar()[1])

class SpeedyEnemy(Enemy):
    def __init__(self, screen, pos):
        super().__init__(screen, pos)
        self.pathSpeed = random.uniform(0.125, 0.2)
        self.image = pygame.image.load('Assets/sonic.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def updateSprite(self):
        self.image = pygame.image.load('Assets/sonic.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.image = pygame.transform.rotate(self.image,
                                             -self.velocity.as_polar()[1])

def wallBetweenPos(pos0, pos1, wall):
    if wall.pos1 == None:
        return False
    (x0, y0) = pos0
    (x1, y1) = pos1
    x = (x0, x1)
    y = (y0, y1)
    (i0, j0) = wall.pos0
    (i1, j1) = wall.pos1
    i = (i0, i1)
    j = (j0, j1)
    if (min(x) <= max(i) and max(x) >= min(i) and max(y) >= min(j)
            and min(y) <= max(j)):
        return True
    return False

class EnemyGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(sprites)

    def update(self, time, walls):
        toBeRemoved = []
        wallsForRemoval = []
        for sprite in self:
            pos0 = copy.copy(sprite.pos)
            sprite.move(time)
            pos1 = sprite.pos
            for wall in walls:
                if wallBetweenPos(pos0, pos1, wall):
                    toBeRemoved.append(sprite)
                    wallsForRemoval.append(wall)
        for sprite in toBeRemoved:
            self.remove(sprite)
        for wall in wallsForRemoval:
            walls.remove(wall)

class Button(pygame.sprite.Sprite):
    def __init__(self, screen, pos, size, message, color, action = None):
        super().__init__()
        self.pos = pos
        self.size = size
        self.message = message
        self.action = action
        self.color = color
        self.font = pygame.font.Font('Linebeam.ttf', 20)
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        textSurf = self.font.render(self.message, True, [255, 255, 255])
        textRect = textSurf.get_rect()
        textRect.center = ((self.size[0]//2, self.size[1]//2))
        self.image.blit(textSurf, textRect)
        self.rect.topleft = pos
        self.screen = screen
        self.pressed = False

    def updateText(self, text):
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        textSurf = self.font.render(text, True, [255, 255, 255])
        textRect = textSurf.get_rect()
        textRect.center = ((self.size[0] // 2, self.size[1] // 2))
        self.image.blit(textSurf, textRect)
        self.rect.topleft = self.pos

    def update(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse) and (click[0] == 0 and self.pressed):
            if self.action != None:
                self.action()
        if click[0] == 1:
            self.pressed = True
        else:
            self.pressed = False

class RoundButton(pygame.sprite.Sprite):
    def __init__(self, screen, pos, radius, message, color, action = None):
        super().__init__()
        self.pos = pos
        self.radius = radius
        self.message = message
        self.action = action
        self.color = color
        self.screen = screen
        self.font = pygame.font.Font('Linebeam.ttf', 20)
        self.refreshSprite()

    def refreshSprite(self):
        self.image = pygame.Surface([self.radius * 2] * 2, pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius),
                           self.radius)
        textSurf = self.font.render(self.message, True, [255, 255, 255])
        textRect = textSurf.get_rect()
        textRect.center = ((self.radius, self.radius))
        self.image.blit(textSurf, textRect)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse) and (click[0] == 1):
            self.radius += self.radius/50
            self.refreshSprite()
            corner = (self.screen.get_width(), self.screen.get_height())
            if (distance(self.pos, corner) < self.radius and
                distance(self.pos, (0, 0)) < self.radius and
                distance(self.pos, (corner[0], 0)) < self.radius and
                distance(self.pos, (0, corner[1])) < self.radius):
                if self.action != None:
                    self.action()
        else:
            if self.radius > 52:
                self.radius -= self.radius/50
                self.refreshSprite()

class Wall(pygame.sprite.Sprite):
    def __init__(self, screen, pos0, pos1):
        super().__init__()
        self.screen = screen
        self.pos0 = pos0
        self.pos1 = pos1

    def draw(self):
        if self.pos1 != None:
            pygame.draw.line(self.screen, [255,0,0], self.pos0, self.pos1)
            self.mass = distance(self.pos0, self.pos1) * 10 ** 3

    def normalizeTo(self, length):
        r = (self.pos1[0] - self.pos0[0], self.pos1[1] - self.pos0[1])
        r = pygame.math.Vector2(r)
        r.scale_to_length(length)
        self.pos1 = (self.pos0[0] + r[0], self.pos0[1] + r[1])
        self.mass = distance(self.pos0, self.pos1) * 10 ** 3

class Title(pygame.sprite.Sprite):
    def __init__(self, screen, message):
        super().__init__()
        self.screen = screen
        self.message = message
        self.width, self.height = screen.get_width(), screen.get_height()
        self.font = pygame.font.Font('Linebeam.ttf', 48)
        self.tran = 255
        self.refreshSprite()

    def refreshSprite(self):
        self.image = self.font.render(self.message, True, [self.tran] * 4)
        self.rect = self.image.get_rect()
        self.rect.center = ((self.width//2, self.height//2))

    def update(self):
        self.tran -= 0.1
        self.refreshSprite()

class Customer(pygame.sprite.Sprite):
    def __init__(self, screen, pos, options):
        super().__init__()

class Parcel(pygame.sprite.Sprite):
    def __init__(self, color, pos, key, velocity):
        super().__init__()
        self.pos = pos
        self.velocity = pygame.math.Vector2(velocity)
        self.mass = 10
        self.radius = 10
        self.key = key
        if self.key == "health":
            self.image = pygame.image.load('Assets/health.png')
            self.image = pygame.transform.scale(self.image, (20, 20))
        elif self.key == "fuel":
            self.image = pygame.image.load('Assets/fuel.png')
            self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.trailPoints = None

    def move(self, time):
        if self.key == "health":
            self.image = pygame.image.load('Assets/health.png')
            self.image = pygame.transform.scale(self.image, (20, 20))
        elif self.key == "fuel":
            self.image = pygame.image.load('Assets/fuel.png')
            self.image = pygame.transform.scale(self.image, (20, 20))
        self.pos = tuple((self.pos[i] + self.velocity[i] * time) for i in range(
            len(self.velocity)))
        self.rect.center = self.pos

    def update(self):
        if self.key == "health":
            self.image = pygame.image.load('Assets/health.png')
            self.image = pygame.transform.scale(self.image, (20, 20))
        elif self.key == "fuel":
            self.image = pygame.image.load('Assets/fuel.png')
            self.image = pygame.transform.scale(self.image, (20, 20))
        self.image = pygame.Surface([self.radius * 2, self.radius * 2],
                                    pygame.SRCALPHA)
        self.image.fill([255, 255, 255, 0])
        pygame.draw.circle(self.image, color, (self.radius, self.radius),
                           self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

class Scavenger(pygame.sprite.Sprite):
    def __init__(self, color, pos):
        super().__init__()
        self.color = color
        self.pos = pos
        self.velocity = pygame.math.Vector2(0.06,0)
        self.mass = 10
        self.radius = 10
        self.image = pygame.image.load('Assets/scavenger.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def move(self, time):
        self.image = pygame.image.load('Assets/scavenger.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.image = pygame.transform.rotate(self.image,
                                             -self.velocity.as_polar()[1])
        self.pos = tuple((self.pos[i] + self.velocity[i] * time) for i in range(
            len(self.velocity)))
        self.rect.center = self.pos

    def update(self):
        self.image = pygame.image.load('Assets/scavenger.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.image = pygame.transform.rotate(self.image,
                                             -self.velocity.as_polar()[1])
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

class Blot(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.density = 7 * 10 ** 3
        self.radius = 25
        self.mass = 0
        self.image = pygame.Surface([self.radius * 2, self.radius * 2],
                                    pygame.SRCALPHA)
        self.image.fill([255, 255, 255, 0])
        pygame.draw.circle(self.image, [255, 0, 0], (self.radius, self.radius),
                           self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = pos