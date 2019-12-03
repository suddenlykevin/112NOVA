#################################################
# NOVA TP2 Deliverable (Algorithms)
#
# Your name: Kevin Xie
# Your andrew id: kevinx
#################################################

import math, copy, random
from classes import *

#################################################
#
# Backtrackers
# CITATION: https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html
# Backtrackers derived from Generic Backtracker
#
################################################

class MapState(object):
    def __init__(self, coords):
        self.coords = coords

    def __hash__(self):
        return hash(str(self.__dict__))

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return (other != None) and self.__dict__ == other.__dict__

# generates a path given player position
class MapGenerator(object):
    def __init__(self, rows, cols, margin, player):
        self.startState = MapState([(0,0)])
        self.rows = rows
        self.cols = cols
        self.margin = margin
        self.player = player

    def getLegalMoves(self, state):
        moves = [(0, -1), (-1, 0), (1, 0),(0, 1)]
        currentPlace = state.coords[-1]
        for move in moves:
            checkCoords = tuple(currentPlace[i] + move[i] for i in range(len(
                    move)))
            if checkCoords in state.coords:
                moves.remove(move)
        random.shuffle(moves)
        return moves

    def doMove(self, state, move):
        newCoords = copy.copy(state.coords)
        newCoords.append(tuple(state.coords[-1][i] + move[i] for i in range(len(
            move))))
        return MapState(newCoords)

    def stateSatisfiesConstraints(self, state):
        lastPos = state.coords[-2]
        currentPos = state.coords[-1]
        if not (0 <= currentPos[0] < self.rows and 0 <= currentPos[1] <
                self.cols):
            return False
        for i in range(1, self.margin + 1):
            if lastPos[0] != currentPos[0]:
                if ((currentPos[0], currentPos[1] + i) in state.coords or
                    (currentPos[0], currentPos[1] - i) in state.coords):
                    return False
            else:
                if ((currentPos[0] + i, currentPos[1]) in state.coords or
                    (currentPos[0] - i, currentPos[1]) in state.coords):
                    return False
        return True

    def isSolutionState(self, state):
        if state.coords[-1] == self.player:
            return True
        return False

    def solve(self):
        self.states = set()
        self.solutionState = self.solveFromState(self.startState)
        if self.solutionState == None:
            return None
        return self.solutionState.coords

    def solveFromState(self, state):
        if state in self.states:
            return None
        self.states.add(state)
        if self.isSolutionState(state):
            return state
        else:
            for move in self.getLegalMoves(state):
                childState = self.doMove(state, move)
                if self.stateSatisfiesConstraints(childState):
                    result = self.solveFromState(childState)
                    if result != None:
                        return result
            return None

class WaveState(object):
    def __init__(self, sequence, n):
        self.sequence = sequence
        self.n = n

    def __hash__(self):
        return hash(str(self.__dict__))

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return (other != None) and self.__dict__ == other.__dict__

# generates a sequence of enemies given difficulty and length
class WaveGenerator(object):
    def __init__(self, diff, length, maxDiff):
        self.startState = WaveState([0] * length, 0)
        self.diff = diff
        self.length = length
        self.maxDiff = maxDiff

    def solveFromState(self, state):
        if state in self.states:
            return None
        self.states.add(state)
        if self.isSolutionState(state):
            return state
        else:
            for move in self.getLegalMoves(state):
                childState = self.doMove(state, move)
                if self.stateSatisfiesConstraints(childState):
                    result = self.solveFromState(childState)
                    if result != None:
                        return result
            return None

    def stateSatisfiesConstraints(self, state):
        return sum(state.sequence) <= self.diff and state.n < self.length

    def doMove(self, state, move):
        newSequence = copy.copy(state.sequence)
        newSequence[state.n] = move
        return WaveState(newSequence, state.n + 1)

    def isSolutionState(self, state):
        return sum(state.sequence) == self.diff

    def getLegalMoves(self, state):
        moves = list(range(self.maxDiff + 1))
        random.shuffle(moves)
        return moves

    def solve(self):
        self.states = set()
        self.solutionState = self.solveFromState(self.startState)
        if self.solutionState == None:
            return None
        return self.solutionState.sequence

#################################################
#
# A* Pathfinding
#
################################################

# Generates 2D list map of given resolution to represent obstacles
def generateMap(screen, objects, dimensions):
    width, height = screen.get_width(), screen.get_height()
    dX, dY = width/dimensions[0], height/dimensions[1]
    map = [["*"] * dimensions[0] for i in range(dimensions[1])]
    for object in objects:
        xRange = range(round(object.rect.left / dX), round(object.rect.right /
                                                         dX))
        yRange = range(round(object.rect.top / dY), round(object.rect.bottom /
                                                        dY))
        for x in xRange:
            for y in yRange:
                map[y][x] = "@"
    return map

class AStarMap(object):
    def __init__(self, screen, map, pos, target):
        self.width, self.height = screen.get_width(), screen.get_height()
        self.map = map
        (self.startX, self.startY) = self.viewToModel(pos)
        (self.targetX, self.targetY) = self.viewToModel(target)

    def viewToModel(self, tuple):
        dX = self.width / len(self.map[1])
        dY = self.height / len(self.map[0])
        result = (round(tuple[0] / dX), round(tuple[1] / dY))
        return result

    def solve(self):
        directions = {(-1, -1): math.pi * 3 / 4,
                      (0, -1): math.pi / 2,
                      (1, -1): math.pi / 4,
                      (-1, 0): math.pi,
                      (1, 0): 0,
                      (-1, 1): math.pi * 5 / 4,
                      (0, 1): math.pi * 3 / 2,
                      (1, 1): math.pi * 7 / 4}

########################################################
#
# Collaborative Diffusion as described in
# CITATION: http://ramblingsofagamedevstudent.blogspot.com/2013/11/for-my-honours-project-this-year-at.html
#
########################################################

# Used to store iterations of collaborative diffusion
class DiffusionState(object):
    def __init__(self, map, iteration):
        self.map = map
        self.iter = iteration

# Class used to store and generate Collaborative Diffusion map given
# obstacles and antiobjects (goals)
class ColDiffMap(object):
    def __init__(self, screen, map, antiobjects):
        self.width, self.height = screen.get_width(), screen.get_height()
        self.map = map
        self.antiobjects = antiobjects

    # converts view coordinates to model coordinates
    def viewToModel(self, tuple):
        dX = self.width / len(self.map[1])
        dY = self.height / len(self.map[0])
        result = (round(tuple[0] / dX), round(tuple[1] / dY))
        return result

    # places antiobjects and diffuses until map is full
    def solve(self):
        for x in range(len(self.map[0])):
            for y in range(len(self.map)):
                if self.map[y][x] == "*":
                    self.map[y][x] = 0
        if len(self.antiobjects) == 0:
            return self.map
        for object in self.antiobjects:
            pos = self.viewToModel(object.pos)
            self.map[pos[1]][pos[0]] = 2048
        self.startState = DiffusionState(self.map, 0)
        result = self.diffuse(self.startState).map
        return result

    # checks if given coordinate is the outermost layer
    def onEdge(self, curmap, x, y):
        if curmap[y][x] == 0:
            return True
        directions = [(-1, -1), (0, -1), (1, -1),
                      (-1, 0), (1, 0),
                      (-1, 1), (0, 1), (1, 1)]
        for d in directions:
            if (0 <= y + d[1] < len(self.map)
                and 0 <= x + d[0] < len(self.map[0])
                and curmap[y + d[1]][x + d[0]] == 0):
                return True
        return False

    # diffuses from given point using collaborative diffusion algorithm
    def diffuseFromPoint(self, state, map, x, y):
        directions = [(-1, -1), (0, -1), (1, -1),
                      (-1, 0), (1, 0),
                      (-1, 1), (0, 1), (1, 1)]
        numNeighbors = 0
        neighborTotal = 0
        # counts number of "neighbors" (excludes walls and obstacles)
        for d in directions:
            if (0 <= y + d[1] < len(state.map)
                and 0 <= x + d[0] < len(state.map[0])
                and state.map[y + d[1]][x + d[0]] != "@"
                and self.onEdge(state.map, x + d[0], y + d[1])):
                numNeighbors += 1
                neighborTotal += state.map[y + d[1]][x + d[0]]
        # empty neighbors are filled with divided scent
        neighborScent = state.map[y][x] / numNeighbors
        # diffusion node is total of neighbor scents / num neighbors
        if state.iter > 0:
            map[y][x] = neighborTotal / numNeighbors
        for d in directions:
            if (0 <= y + d[1] < len(state.map)
                and 0 <= x + d[0] < len(state.map[0])
                and state.map[y + d[1]][x + d[0]] == 0
                and self.onEdge(state.map, x + d[0], y + d[1])):
                map[y + d[1]][x + d[0]] = neighborScent

    # checks if map is filled with values
    def isFilled(self, map):
        for row in map:
            if row.count(0) > 1:
                return False
        return True

    # recursively diffuses antiobjects until map is filled
    def diffuse(self, state):
        if self.isFilled(state.map):
            return state
        else:
            newMap = copy.deepcopy(state.map)
            for x in range(len(state.map[0])):
                for y in range(len(state.map)):
                    if (state.map[y][x] != "@" and state.map[y][x] != 0 and
                        self.onEdge(state.map, x, y)):
                        self.diffuseFromPoint(state, newMap, x, y)
            return self.diffuse(DiffusionState(newMap, state.iter + 1))