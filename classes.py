import math

import pygame

from mapgenerator import *

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
        self.health = 10
        self.image = pygame.Surface([self.screen.get_width()/8] * 2,
                                    pygame.SRCALPHA)
        self.image.fill([255, 255, 255, 0])
        self.radius = self.screen.get_width()/16
        pygame.draw.circle(self.image, [0, 0, 255],
                           (self.screen.get_width()/16,
                            self.screen.get_width()/16),
                           self.screen.get_width()/16)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

    def drawGUI(self):
        ratio = self.fuel / 10 ** 6
        fuelBar = pygame.Rect(0, self.screen.get_height() - 10,
                              self.screen.get_width() * ratio, 10)
        pygame.draw.rect(self.screen, [255, 127, 0], fuelBar)
        healthRatio = self.health / 10
        healthBar = pygame.Rect(0, self.screen.get_height() - 20,
                                self.screen.get_width() * healthRatio, 10)
        pygame.draw.rect(self.screen, [255, 0, 32], healthBar)

    def draw(self):
        self.screen.blit(self.image,self.rect)

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
                spritestrip.append(spritesheet.crop((dx * i, dy * strip,
                                                     dx * (i + 1),
                                                     dy * (strip + 1))))
            sprites.append(spritestrip)
        # scales each sprite down by half
        for row in range(spriteAnims):
            for col in range(maxFrames):
                sprites[row][col] = sprites[row][col].resize(48, 52)
        return sprites

class Planet(pygame.sprite.Sprite):
    def __init__(self, screen, pos):
        super().__init__()
        self.screen = screen
        self.pos = pos
        self.density = 3 * 10 ** 4
        self.radius = 0
        self.mass = 0

    def retrieveSprites(self):
        pass

    def update(self, rate):
        self.radius += rate
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
        self.velocity = pygame.math.Vector2(0,0)
        self.mass = 10
        self.radius = 10
        self.image = pygame.Surface([self.radius * 2, self.radius * 2],
                                    pygame.SRCALPHA)
        self.image.fill([255, 255, 255, 0])
        pygame.draw.circle(self.image, [128] * 3, (self.radius, self.radius),
                           self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def move(self, time):
        self.pos = tuple((self.pos[i] + self.velocity[i] * time) for i in range(
            len(self.velocity)))
        self.rect.center = self.pos

    def draw(self):
        pass

class PathPiece(pygame.sprite.Sprite):
    directions = [[0.1,0], [0,0.1], [-0.1,0], [0,-0.1]]
    def __init__(self, pos, size, orientation, corner):
        super().__init__()
        self.corner = corner
        self.size = size
        self.image = pygame.Surface([size] * 2)
        self.image.fill([32,32,64])
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.direction = PathPiece.directions[orientation]

class Map(pygame.sprite.Group):
    def __init__(self, screen, diff):
        self.coords = MapGenerator(8, 8, diff, (7, 7)).solve()
        self.screen = screen
        self.tileSize = self.screen.get_width() // 9
        self.spriteMap = self.retrieveSprites()
        super().__init__(self.spriteMap)

    def retrieveSprites(self):
        spriteList = set()
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
            corner = False
            if i > 0:
                if (self.coords[i][0] != self.coords[i-1][0] and
                        orientation in (1,3)) or (self.coords[i][1] !=
                        self.coords[i-1][1] and orientation in (0,2)):
                    corner = True
            transCoord = [elem * self.tileSize for elem in self.coords[i]]
            spriteList.add(PathPiece(transCoord, self.tileSize, orientation,
                                     corner))
        return spriteList

# test subclass of enemy
class AcceleratingEnemy(Enemy):
    def __init__(self, screen, pos):
        super().__init__(screen, pos)

class EnemyGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(sprites)

    def update(self, time):
        for sprite in self:
            sprite.move(time)

class Button(pygame.sprite.Sprite):
    def __init__(self, screen, pos, size, message, color, action = None):
        super().__init__()
        self.pos = pos
        self.size = size
        self.message = message
        self.action = action
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.screen = screen

    def update(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse) and (click[0] == 1):
            if self.action != None:
                self.action()

class RoundButton(pygame.sprite.Sprite):
    def __init__(self, screen, pos, radius, message, color, action = None):
        super().__init__()
        self.pos = pos
        self.radius = radius
        self.message = message
        self.action = action
        self.color = color
        self.screen = screen
        self.refreshSprite()

    def refreshSprite(self):
        self.image = pygame.Surface([self.radius * 2] * 2, pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius),
                           self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse) and (click[0] == 1):
            self.radius += 3
            self.refreshSprite()
            corner = (self.screen.get_width(), self.screen.get_height())
            if (distance(self.pos, corner) < self.radius and
                distance(self.pos, (0, 0)) < self.radius):
                if self.action != None:
                    self.action()
        else:
            if self.radius > 52:
                self.radius -= 3
                self.refreshSprite()