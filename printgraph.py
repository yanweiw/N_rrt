import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

def printgraph(G, xmaxinx, ymaxidx):
    # G is a dict of tuples, key is vert while value is its parent
    verts = []
    codes = []

    for q in G:
        verts.append(list(q))
        verts.append(list(G[q]))
        codes.append(Path.MOVETO)
        codes.append(Path.LINETO)

    print verts
    print codes

    fig = plt.figure()
    path = Path(verts, codes)
    patch = patches.PathPatch(path)
    ax = fig.add_subplot(111)
    ax.add_patch(patch)
    ax.set_xlim([0, xmaxinx])
    ax.set_ylim([0, ymaxidx])
    plt.show()
