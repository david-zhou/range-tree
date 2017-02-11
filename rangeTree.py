import random, math, time
from mpl_toolkits.mplot3d import Axes3D

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pylab as plt


maxRange = 1000

class Node:
    def __init__(self, data, currentDimension = 1):
        self.subtree = None
        self.data = data
        self.parent = None
        self.left = None
        self.right = None
    
    def __str__(self):
        return str(self.data)
        
    def lt(self, other, k):
        return self.data[k] < other.data[k]
        
    def gt(self, other, k):
        return self.data[k] > other.data[k]
    
    def eq(self, other, k):
        return self.data[k] == other.data[k]
        
    def ne(self, other, k):
        return self.data[k] != other.data[k]
        
    def ge(self, other, k):
        return self.data[k] >= other.data[k]
        
    def le(self, other, k):
        return self.data[k] <= other.data[k]
    
    def getPredecessor(self):
        if self.left:
            return self.left.getMax()
        else:
            return self.data
            
    def getMax(self):
        if self.right:
            return self.right.getMax()
        else:
            return self.data

    def printTree(self):
        if self.left:
            print("Node with value {}".format(self))
            print("{} left = ".format(self), end=" ")
            self.left.printTree()
            print("{} right = ".format(self), end=" ")
            self.right.printTree()
        else:
            print("leaf with element {}".format(self))
            
    def search(self, n, k):
        if self.left:
            if self.data[k] >= n:
                return [0] + self.left.search(n, k)
            else:
                return [1] + self.right.search(n, k)
        else:
            return []
            
    def getLeaves(self):
        if not self.left:
            return [self.data]
        else:
            return self.left.getLeaves() + self.right.getLeaves()
            
    def searchLower(self, n, k, steps):
        if self.left:
            current = self.left
        else:
            if self.data[k] >=n:
                return [self]
            else:
                return []
        blackNodes = []
        for s in steps:
            if s == 0:
                blackNodes.append(current.right)
                current = current.left
            else:
                current = current.right
        if current.data[k] >= n:
            blackNodes.append(current)
        return blackNodes
        
    def searchUpper(self, n, k, steps):
        if self.right:
            current = self.right
        else:
            if self.data[k] <= n:
                return [self]
            else:
                return []
        blackNodes = []
        for s in steps:
            if s == 0:
                current = current.left
            else:
                blackNodes.append(current.left)
                current = current.right
        if current.data[k] <= n:
            blackNodes.append(current)
        return blackNodes

def buildTree(arr, currentDim, dimension):
    if len(arr) == 1:
        if currentDim < dimension - 1:
            arr[0].subtree = buildTree(arr, currentDim + 1, dimension)
        return arr[0]
    else:
        nodes = splitLevel(arr)
        n1 = buildTree(nodes[0], currentDim, dimension)
        n2 = buildTree(nodes[1], currentDim, dimension)
        newNode = Node(n1.getMax())
        newNode.left = n1
        newNode.right = n2
        n1.parent = newNode
        n2.parent = newNode
        if currentDim < dimension - 1:
            leaves = newNode.getLeaves()
            newLeaves = []
            leaves.sort(key=lambda x:x[currentDim + 1])
            for l in leaves:
                newLeaves.append(Node(l))
            newNode.subtree = buildTree(newLeaves, currentDim + 1, dimension)
        return newNode
        
def findSplitNode(steps1, steps2):
    l = min(len(steps1), len(steps2))
    for i in range(l):
        if steps1[i] != steps2[i]:
            return i
    return l
    
def splitLevel(nodes):
    l = len(nodes)
    mid = math.floor(l/2)
    n1 = nodes[:mid]
    n2 = nodes[mid:]
    return [n1, n2]

def searchKDims(ranges, tree, dimensions):
    blackNodesByDimension = [[] for d in range(dimensions+1)]
    blackNodesByDimension[0].append(tree)
    for k in range(dimensions):
        for actualTree in blackNodesByDimension[k]:
            temp = actualTree
            if k != 0:
                actualTree = actualTree.subtree
            lowerPath = actualTree.search(ranges[k][0], k)
            upperPath = actualTree.search(ranges[k][1], k)
            splitIndex = findSplitNode(lowerPath, upperPath)
            splitNode = actualTree
            blackNodes = []
            for j in range(splitIndex):
                if lowerPath[j] == 0:
                    splitNode = splitNode.left
                else:
                    splitNode = splitNode.right
            if lowerPath == upperPath:
                if splitNode.data[k] <= ranges[k][1] and splitNode.data[k] >= ranges[k][0]:
                    blackNodes = [splitNode]
            else:
                lowerPath = lowerPath[(splitIndex + 1):]
                upperPath = upperPath[(splitIndex + 1):]
                blackNodes1 = splitNode.searchLower(ranges[k][0], k, lowerPath)
                blackNodes2 = splitNode.searchUpper(ranges[k][1], k, upperPath)
                blackNodes = list(set(blackNodes1) | set(blackNodes2))
            for bn in blackNodes:
                blackNodesByDimension[k+1].append(bn)
    finalNodes = []
    for bn in blackNodesByDimension[dimensions]:
        leaves = bn.getLeaves()
        for l in leaves:
            finalNodes.append(l)
    return finalNodes

def createRandomPoints(n, dimension, default = 2):
    points = []
    for i in range(n):
        p = []
        for j in range(dimension):
            coord = random.randrange(-maxRange, maxRange)
            p.append(coord)
        if default == 1:
            p.append(0)
        points.append(p)
    return points

def plotPoints(points, color = 'bo'):
    for p in points:
        plt.plot(p[0], p[1], color)

def plotRanges(ranges, color = 'g'):
    x1 = ranges[0][0]
    x2 = ranges[0][1]
    y1 = ranges[1][0]
    y2 = ranges[1][1]
    plt.plot([x1, x1], [-maxRange, maxRange], color=color, linestyle='-', linewidth=1)
    plt.plot([x2, x2], [-maxRange, maxRange], color=color, linestyle='-', linewidth=1)
    plt.plot([-maxRange, maxRange], [y1, y1], color=color, linestyle='-', linewidth=1)
    plt.plot([-maxRange, maxRange], [y2, y2], color=color, linestyle='-', linewidth=1)
    
def plotPoints3d(points, color = 'b', marker = 'o'):
    px = [p[0] for p in points]
    py = [p[1] for p in points]
    pz = [p[2] for p in points]
    ax.scatter(px, py, pz, c=color, marker = marker)
        
def plotRanges3d(ranges, color = 'g'):
    x1 = ranges[0][0]
    x2 = ranges[0][1]
    y1 = ranges[1][0]
    y2 = ranges[1][1]
    z1 = ranges[2][0]
    z2 = ranges[2][1]
    ax.plot([x1, x2], [y1, y1], [z1, z1], c = color)
    ax.plot([x1, x1], [y1, y2], [z1, z1], c = color)
    ax.plot([x2, x1], [y2, y2], [z1, z1], c = color)
    ax.plot([x2, x2], [y2, y1], [z1, z1], c = color)
    
    ax.plot([x1, x2], [y1, y1], [z2, z2], c = color)
    ax.plot([x1, x1], [y1, y2], [z2, z2], c = color)
    ax.plot([x2, x1], [y2, y2], [z2, z2], c = color)
    ax.plot([x2, x2], [y2, y1], [z2, z2], c = color)
    
    ax.plot([x1, x1], [y1, y1], [z1, z2], c = color)
    ax.plot([x1, x1], [y2, y2], [z1, z2], c = color)
    ax.plot([x2, x2], [y2, y2], [z1, z2], c = color)
    ax.plot([x2, x2], [y1, y1], [z1, z2], c = color)
    
dimension = int(input("Dimension: "))
n = int(input("Cantidad de puntos: "))

if dimension == 1:
    ar = createRandomPoints(n, dimension, 1)
else:
    ar = createRandomPoints(n, dimension)

startTime = time.time()
#dimension = 2
ar.sort(key=lambda x:x[0])
arr = []

for x in ar:
    arr.append(Node(x))

tree = buildTree(arr, 0, dimension)
endTime = time.time()

print("Tiempo de construcción del arbol: {} ".format(endTime - startTime))


while True:
    if dimension <= 2:
        plotPoints(ar)
    elif dimension == 3:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        plotPoints3d(ar)

    plt.show()

    print("Puntos = {}".format(ar))
    
    ranges = []

    for i in range(dimension):
        down, up = map(int, input("Rango de la dimension {}, separado por espacio: ".format(i+1)).split())
        ranges.append([down, up])
    if dimension == 1:
        ranges.append([-maxRange, maxRange])
    
    startTime = time.time()
    
    finalNodes = searchKDims(ranges, tree, dimension)

    print("Los puntos en el rango son: ")
    for nodes in finalNodes:
        print(nodes)
        
    endTime = time.time()
    print("Tiempo de búsqueda: {} ".format(endTime - startTime))

    if dimension <= 2:
        plotPoints(ar)
        points = []
        for node in finalNodes:
            points.append(node)
        plotPoints(points, 'ro')
        plotRanges(ranges)
        plt.show()
    elif dimension == 3:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        originalAr = []
        for p in ar:
            if p not in finalNodes:
                originalAr.append(p)
        plotPoints3d(originalAr)
        points = []
        for node in finalNodes:
            points.append(node)
        plotPoints3d(points, 'r', '^')
        plotRanges3d(ranges)
        plt.show()
