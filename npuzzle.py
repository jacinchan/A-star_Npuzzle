# author: jacin
# date: Feb,2016
import math
from queue import PriorityQueue as pq
from time import time


class Node(object):
    def __init__(self, parent=None, lastaction=None):
        self._parent = parent
        self._lastaction = lastaction
        self._cost = parent.cost + 1 if parent else 0
        self._distance = None

    def __eq__(self, other):
        return other.priority == self.priority

    def __lt__(self, other):
        return self.priority < other.priority

    @property
    def priority(self):
        return self._cost + self._distance

    @property
    def parent(self):
        return self._parent

    @property
    def cost(self):
        return self._cost

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    @property
    def lastaction(self):
        return self._lastaction

    @lastaction.setter
    def lastaction(self, value):
        self._lastaction = value

    @property
    def isfinished(self):
        return self._distance == 0


class Puzzle(Node):
    def __init__(self, parent=None, lastaction=None):
        super().__init__(parent, lastaction)
        if parent:
            self._size = parent.size
            self._goat = parent.goat
            self._state = parent.getstateafteraction(lastaction)
        else:
            self._size = 0
            self._goat = []
            self._state = []

    def initstate(self, state):
        self._size = int(math.sqrt(len(state)))
        self._goat = list(range(self._size**2))
        self._state = state
        # self._state = self._goat.copy()
        # random.shuffle(self._state)

    def __str__(self):
        return '{0} cost:{1} dist:{2}'.format(self.state, self.cost, self.distance)

    # @property
    # def isfinished(self):
    #     return self._goat == self._state

    @property
    def size(self):
        return self._size

    @property
    def state(self):
        return self._state

    @property
    def goat(self):
        return self._goat

    def getpossibleactions(self):
        t = []
        zeroindex = self._state.index(0)
        if zeroindex < (self._size * self._size - self._size):
            t.append('up')
        if zeroindex > (self._size - 1):
            t.append('down')
        if (zeroindex + 1) % self._size:
            t.append('left')
        if (zeroindex + 3) % self._size:
            t.append('right')
        return t

    def getstateafteraction(self, action):
        zeroindex = self._state.index(0)
        state = self._state.copy()
        if action == 'up':
            targetindex = zeroindex + self._size
        elif action == 'down':
            targetindex = zeroindex - self._size
        elif action == 'left':
            targetindex = zeroindex + 1
        elif action == 'right':
            targetindex = zeroindex - 1

        state[zeroindex], state[targetindex] = state[
            targetindex], state[zeroindex]
        return state

    def getmisplacetitlecount(self):
        count = 0
        for i, v in enumerate(self._state):
            if i != v:
                count += 1
        return count

    def getmanhattandist(self):
        dist = 0
        for i, v in enumerate(self._state):
            ix = i % self._size
            vx = v % self._size
            iy = i // self._size
            vy = v // self._size
            dist += abs(ix - vx) + abs(iy - vy)
        return dist


class Astar(object):
    def __init__(self, puzzle, method='manhattan'):
        self._puzzle = puzzle
        self.method = method
        self.totalnodecount = 0

    def newnode(self, parent=None, lastaction=None, puzzle=None):
        if puzzle:
            n = puzzle
        else:
            n = Puzzle(parent, lastaction)
        if self.method == 'manhattan':
            n.distance = n.getmanhattandist()
        if self.method == 'misplace':
            n.distance = n.getmisplacetitlecount()
        return n

    def popbestnode(self, l):
        # print('%d nodes in open list' % len(l))
        i, p = 0, l[0].priority
        for c, n in enumerate(l):
            if n.priority < p:
                i, p = c, n.priority
            # print('node %d -> state: %s cost:%d, dist:%d, priority:%d' %
            #       (c, n.state, n.cost, n.distance, n.priority))
        # print('pick node %d' % i)
        return l.pop(i)

    def extendnode(self, n):
        t = []
        actions = n.getpossibleactions()
        for action in actions:
            newnode = self.newnode(n, action)
            t.append(newnode)
        return t

    def solve(self):
        initNode = self.newnode(puzzle=self._puzzle)
        listopen = pq()
        listclose = []
        listopen.put(initNode)
        while listopen:
            n = listopen.get()
            listclose.append(n)
            if n.isfinished:
                self.totalnodecount = listopen.qsize() + len(listclose)
                return n
            for ext in self.extendnode(n):
                listopen.put(ext)
        return False

    def printresult(self, n):
        c = n
        t = []
        while c.lastaction:
            t.append(c.lastaction)
            c = c.parent
        print(', '.join(reversed(t)))
        print('search depth:' + str(len(t)))
        print('generated %d nodes' % self.totalnodecount)
        #################

        def ebf(b, d):
            return sum(map(lambda x: b ** x, range(d + 1)))
        #################
        b = 1
        while ebf(b, len(t)) < self.totalnodecount:
            b += 0.005
        print('Effective Branching Factor:' + str(b))
        # while c:
        #     print(c)
        #     c = c.parent


if __name__ == '__main__':
    puzzle = Puzzle()

    # puzzle.initstate([1, 2, 0, 3, 4, 5, 6, 7, 8])
    puzzle.initstate([2, 5, 4, 6, 1, 3, 0, 7, 8])
    # puzzle.initstate([2, 5, 4, 7, 6, 0, 8, 3, 1])
    # puzzle.initstate([7, 2, 4, 5, 0, 6, 8, 3, 1])

    manhattanastar = Astar(puzzle, method='manhattan')
    print('init state:')
    print(puzzle.state)
    print('')

    print('start searching, using ' + manhattanastar.method)
    cutime = time()
    n = manhattanastar.solve()
    delta = time() - cutime
    delta = str(delta) + 's' if delta else 'less than 0.0000001s'
    print('solved, used ' + delta)
    if n:
        manhattanastar.printresult(n)
    print('')

    misplaceastar = Astar(puzzle, method='misplace')
    print('start searching, using ' + misplaceastar.method)
    cutime = time()
    n = misplaceastar.solve()
    delta = time() - cutime
    delta = str(delta) + 's' if delta else 'less than 0.0000001s'
    print('solved, used ' + delta)
    if n:
        misplaceastar.printresult(n)
