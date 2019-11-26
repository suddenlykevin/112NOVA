import copy, random
from classes import *

# https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html#Backtracking
class MapState(object):
    def __init__(self, coords):
        self.coords = coords

    def __hash__(self):
        return hash(str(self.__dict__))

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return (other != None) and self.__dict__ == other.__dict__

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
    def __init__(self, sequence):
        self.sequence = sequence

    def __hash__(self):
        return hash(str(self.__dict__))

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return (other != None) and self.__dict__ == other.__dict__

class WaveGenerator(object):
    def __init__(self, diff, length, maxDiff):
        self.startState = MapState([0] * length)
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
        pass

    def doMove(self, state, move):
        pass

    def isSolutionState(self, state):
        pass

    def getLegalMoves(self, state):
        pass

    def solve(self):
        self.states = set()
        self.solutionState = self.solveFromState(self.startState)
        if self.solutionState == None:
            return None
        return self.solutionState.sequence