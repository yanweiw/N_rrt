import numpy as np
import random as rd
from scipy.spatial import distance as dist
from scipy.misc import imread
import math

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

# how big is our world? Expecting a square world
SIZE = 100
navigation = [] # path connecting qinit to target
ax = plt.subplot(111)
PERCENTAGE_SPACE_TO_LEAVE = 0.03 #controls how much space in periphery of a vertice to leave

# world records the center coordinates and radius of circular obstacles
# G is a graph of current vertices and edges, implemented by dict G[vertex] = parent vertex

def rand_conf():
    '''
    generate random positions on the map
    '''
    return (rd.randint(0,SIZE),rd.randint(0,SIZE))

def near_vert(qrand, G):
    '''
    find the nearest vertex
    '''
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
    '''
    check if edge between qnear and qrand collides with world obstacles
    '''
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
        if d <= r + SIZE * PERCENTAGE_SPACE_TO_LEAVE:
            return True

    for seg in G:
        '''
        check edges do not cross each other
        '''
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

def limitrange(qrand, qnear, qdelta):
    '''
    discard explorations that are too close, within PERCENTAGE_SPACE_TO_LEAVE * SIZE
    cap the exploration length by the remainder of length / (SIZE * qdelta)
    '''
    d = dist.euclidean(qrand,qnear)
    if d < SIZE * PERCENTAGE_SPACE_TO_LEAVE:
        return (-1, -1) #discard
    newd = d%(SIZE*qdelta)
    qnew = qnear + (qrand - qnear)*newd/d
    return tuple(qnew)

def navigate(G, qinit, target):
    '''
    create navigation path
    '''
    global navigation
    navigation.append(target)
    next = target
    while next != qinit:
        next = G[next]
        navigation.append(next)

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

def createworld():
    '''
    create a world map of 10 circular obstacles of random size and postion
    '''
    world = generate_circles(10, 8, 3)
    return world

def worldblockstart(world,qinit,target):
    '''
    check if the qinit and target coincide with world obstacles
    '''
    for circle in world:
        if dist.euclidean(circle[1:],qinit) <= circle[0] + SIZE*PERCENTAGE_SPACE_TO_LEAVE:
            return True
        if target != (-1,-1):
            if dist.euclidean(circle[1:],target) <= circle[0] + SIZE*PERCENTAGE_SPACE_TO_LEAVE:
                return True
    return False

def printworld(worldfile, start, end):
    '''
    print world, if worldfile is 'None', print world as circles
    otherwise, print world as binary image
    '''
    global SIZE
    global ax

    world = []
    if worldfile == 'None':
        #create world
        while True:
            SIZE = 100
            world = createworld()
            if not worldblockstart(world,start,end):
                break
        #draw the circles
        fcirc = lambda x: patches.Circle((x[1],x[2]), radius=x[0], fill=True, alpha=1, fc='k', ec='k')
        circs = [fcirc(x) for x in world]
        for c in circs:
            ax.add_patch(c)
    else:
        binaryworld = imread(worldfile)
        binaryworld = np.flipud(binaryworld)
        SIZE = binaryworld.shape[0]
        for x in range(SIZE):
            for y in range(SIZE):
                if binaryworld[y][x][0] == 0:
                    world.append([0.5, x+0.5, y+0.5])
        world = np.asarray(world)
        print 'got here'
        if worldblockstart(world, start, end):
            raise ValueError("start and end are not in open space")

        #draw the binary image
        plt.imshow(binaryworld[:,:,0], cmap=plt.cm.Purples_r, interpolation='nearest',origin='lower',extent=[0,SIZE,0,SIZE])

    return world

def printgraph(start, end, G, world):
    '''
    print navigation from start to end
    '''
    global navigation
    global ax

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
    plt.plot(start[0], start[1], marker='o', alpha=.5, markersize=18, color='red')
    # ax.text(start[0], start[1], 'start')
    plt.plot(end[0], end[1], marker='o', alpha=.5, markersize=18, color='green')
    # ax.text(end[0], end[1], 'end')
    if navigation != []:
    # if end != (-1,-1):
        stops = []
        moves = []
        for i, q in enumerate(navigation[:-1]):
            stops.append(q)
            stops.append(navigation[i+1])
            moves.append(Path.MOVETO)
            moves.append(Path.LINETO)
        route = Path(stops, moves)
        patch2 = patches.PathPatch(route, color='orange', alpha=.5, lw=5)
        ax.add_patch(patch2)

def showpath():
    global ax
    global SIZE
    plt.xlim([0,SIZE])
    plt.ylim([0,SIZE])
    # plt.xticks(range(0,SIZE + 1))
    # plt.yticks(range(0,SIZE + 1))
    ax.set_aspect('equal')
    # ax.set_xticklabels(['x'])
    # ax.set_yticklabels([])
    plt.show(block=False)

def rrt(qinit, target, qdelta, world, K):
    '''
    implementation of rrt
    '''
    # initialize graph as dict of tuples as coordinates
    G = {qinit:qinit} # use self-reference to indicate start
    showpath()
    k = 0
    while k < K:
        qrand = rand_conf()
        qnear = near_vert(qrand, G)
        if qnear == (-1, -1): #(-1,-1) are cases to ignore
            continue
        qnew = limitrange(np.asarray(qrand), np.asarray(qnear),qdelta)
        if qnew == (-1, -1):  # too short of an exploration
            continue
        if G.has_key(qnew): # discard repeated vertex
            continue
        if collide(qnear, qnew, world, G):
            continue
        G[qnew] = qnear
        if target != (-1,-1):
            if dist.euclidean(qnew, target) <= SIZE*PERCENTAGE_SPACE_TO_LEAVE: # close enough to target
                if target != qnew:
                    G[target] = qnew
                navigate(G, qinit, target)
                return G
        k += 1

    return G

def findpath(qdelta, start=(50,50), end=(-1,-1), worldfile='None', K=1000, printedges=True):
    '''
    main function to run rrt capped at 1000 iterations by default
    with the option of changing K, omitting end to just print graph
    and giving printedges False value to just print world
    Also, with the option to provide your own world, expecting binary square image
    '''
    global navigation
    global SIZE
    global ax

    plt.close()
    ax = plt.subplot(111)
    navigation = [] # reinitialize this global variable everytime

    world = printworld(worldfile, start, end)

    if printedges:
        G = rrt(start, end, qdelta, world, K)
        printgraph(start, end, G, worldfile)

    showpath()
