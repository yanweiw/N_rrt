import numpy as np
import random as rd
from scipy.spatial import distance as dist
import math

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

# how big is our world?
SIZE = 100
qinit = (50,50)
navigation = []


def rand_conf():
    return (rd.randint(0,SIZE),rd.randint(0,SIZE))

def near_vert(qrand, G):
    l2dist = math.sqrt(SIZE**2+SIZE**2) #max distance on the board
    qnear = (-1,-1) # edge case, no nearest vertex is found
    for q in G:
        if q == qrand:
            continue
        currdist = dist.euclidean(q, qrand)
        if currdist <= l2dist:
            l2dist = currdist
            qnear = q
    return qnear

def collide(qnear, qrand, world, G):
    # collision check, world is array of circles currently
    x1 = qrand[0]
    y1 = qrand[1]
    x2 = qnear[0]
    y2 = qnear[1]
    for circle in world:
        r = circle[0]
        x3 = circle[1]
        y3 = circle[2]
        u = ((x3-x1)*(x2-x1) + (y3-y1)*(y2-y1))/((x2-x1)**2+(y2-y1)**2)
        if u < 1 and u > 0:
            x = x1+u*(x2-x1)
            y = y1+u*(y2-y1)
            d = dist.euclidean((x,y),(x3,y3))
        elif u >= 1:
            d = dist.euclidean((x3,y3),(x2,y2))
        else:
            d = dist.euclidean((x3,y3),(x1,y1))
        if d <= r + SIZE * 0.01:
            return True

    for seg in G:
        x3 = seg[0]
        y3 = seg[1]
        x4 = G[seg][0]
        y4 = G[seg][1]
        de = ((y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)) #denominator
        if de == 0:
            continue
        u1 = ((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3)) / de
        u2 = ((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3)) / de
        if (u1==0 and u2==0) or (u1==1 and u2==1) or (u1==1 and u2 ==0) or (u1==0 and u2==1):
            continue
        if  (0 <= u1 <= 1) and (0 <= u2 <= 1):
            return True

    return False

def limitrange(qrand, qnear,qdelta):
    d = dist.euclidean(qrand,qnear)
    if d < SIZE * 0.02:
        return (-1, -1)
    newd = d%(SIZE*qdelta)
    qnew = qnear + (qrand - qnear)*newd/d
    return tuple(qnew)

def navigate(G, qinit, target):
    global navigation
    navigation.append(target)
    next = target
    while next != qinit:
        next = G[next]
        navigation.append(next)

def rrt(qinit, target, qdelta, world, K):
    # initialize graph as dict of tuples as coordinates
    G = {qinit:qinit} # use self-reference to indicate start

    k = 0
    while k < K:
        qrand = rand_conf()
        qnear = near_vert(qrand, G)
        if qnear == (-1, -1):
            continue
        qnew = limitrange(np.asarray(qrand), np.asarray(qnear),qdelta)
        if qnew == (-1, -1):
            continue    # too short of an exploration
        if G.has_key(qnew):
            continue
        if collide(qnear, qnew, world, G):
            continue
        G[qnew] = qnear
        if dist.euclidean(qnew, target) <= SIZE*0.02:
            G[target] = qnew
            navigate(G, qinit, target)
            return G
        k += 1

    return G

def generate_circles(num, mean, std):
    """
    This function generates /num/ random circles with a radius mean defined by
    /mean/ and a standard deviation of /std/.

    The circles are stored in a num x 3 sized array. The first column is the
    circle radii and the second two columns are the circle x and y locations.
    """
    circles = np.zeros((num,3))
    # generate circle locations using a uniform distribution:
    circles[:,1:] = np.random.uniform(mean, SIZE-mean, size=(num,2))
    # generate radii using a normal distribution:
    circles[:,0] = np.random.normal(mean, std, size=(num,))
    return circles

# generate circles:
def createworld():
    world = generate_circles(10, 8, 3)
    return world

def printgraph(start, end, G, world, printedges=True):
    # G is a dict of tuples, key is vert while value is its parent
    global navigation
    plt.close()
    ax = plt.subplot(111)

    fcirc = lambda x: patches.Circle((x[1],x[2]), radius=x[0], fill=True, alpha=1, fc='k', ec='k')
    circs = [fcirc(x) for x in world]
    for c in circs:
        ax.add_patch(c)

    if printedges:
        # print exploration edges
        verts = []
        codes = []
        for q in G:
            verts.append(list(q))
            verts.append(list(G[q]))
            codes.append(Path.MOVETO)
            codes.append(Path.LINETO)
        path = Path(verts, codes)
        patch = patches.PathPatch(path)
        ax.add_patch(patch)
        # print navigation from start to end
        stops = []
        moves = []
        for i, q in enumerate(navigation[:-1]):
            stops.append(q)
            stops.append(navigation[i+1])
            moves.append(Path.MOVETO)
            moves.append(Path.LINETO)
        route = Path(stops, moves)
        patch2 = patches.PathPatch(route, color='orange', lw=2)
        ax.add_patch(patch2)
        plt.plot(start[0], start[1], marker='o', color='red', lw=2)
        plt.plot(end[0], end[1], marker='o', color='blue', lw=2)
        ax.text(start[0], start[1], 'start')
        ax.text(end[0], end[1], 'end')

    plt.xlim([0,SIZE])
    plt.ylim([0,SIZE])
    plt.xticks(range(0,SIZE + 1))
    plt.yticks(range(0,SIZE + 1))
    ax.set_aspect('equal')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    plt.show(block=False)

def worldblockstart(world,qinit,target,qdelta):
    for circle in world:
        if dist.euclidean(circle[1:],qinit) <= circle[0] + SIZE*0.01:
            return True
        if dist.euclidean(circle[1:],target) <= circle[0] + SIZE*0.01:
            return True
    return False

def findpath(start, end, qdelta, K=SIZE**2, printedges=True):
    global navigation
    navigation = [] # reinitialize this global variable everytime

    while True:
        world = createworld()
        if not worldblockstart(world,start,end,qdelta):
            break

    G = rrt(start, end, qdelta, world, K)
    printgraph(start, end, G, world, printedges)
