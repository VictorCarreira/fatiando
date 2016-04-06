"""
"""
from __future__ import division, unicode_literals, print_function
from future.builtins import super, object, range
import numpy as np

from ..inversion import Misfit


class PlantingMagnetic(object):
    pass

class _PlantingAlgorithm(object):

    def predicted(self, p):
        pass

    def shape_of_anomaly(self, p):
        pass

    def config(self):
        pass


    def fit(self):
        pass


class PlantingGravity(Misfit, _PlantingAlgorithm):
    """
    """

    def __init__(self, x, y, z, data, mesh, field='gz'):
        super().__init__(data=data, nparams=mesh.size, islinear=False)
        self.x = x
        self.y = y
        self.z = z
        self.mesh = mesh
        self.field = field
        self.seeds = None
        self.mu = None
        self.tol = None
        self.effects = None

    def predicted(self, p):
        pred = np.zeros(self.ndata)
        for i in np.nonzero(p)[0]:
            if i not in self.effects:
                self.effects[i] = self.kernel(self.x, self.y, self.z,
                                              [self.mesh[i]], dens=p[i])
            pred += self.effects[i]
        return pred

    def config(self, seeds, compactness, tol):
        """
        """
        self.seeds = _sow(seeds, self.mesh)
        self.compactness = compactness
        self.mu = compactness/(sum(mesh.shape)/3)
        self.tol = tol
        return self

    def fit(self):
        """
        """
        p = np.zeros(self.nparams, dtype=np.float)
        added = set()
        for s in self.seeds:
            p[s.index] = s.prop
            added.add(s.index)
        neighbors = {}
        allneighbors = set()
        for s in self.seeds:
            tmp = s.neighbors.difference(allneighbors).difference(added)
            all_neighbors.add(tmp)
            neighbors[s] = tmp
        misfit = self.value(p)
        compactness = 0
        goal = self.shape_of_anomaly(p) + self.mu*compactness
        for iteration in range(self.nparams - len(self.seeds)):
            grew = False
            for s in self.seeds:
                best = None
                for n in neighbors[s]:
                    p[n.i] = n.prop
                    newmisfit = self.value(p)
                    if (newmisfit >= misfit or
                        abs(newmisfit - misfit)/misfit < self.tol):
                        goals.append(np.inf)
                        continue
                    newcompactness = compactness + n.distance_to(s)
                    newgoal = self.shape_of_anomaly(p) + mu*compactness
                    p[n.i] = 0
                    if best is None or newgoal < bestgoal:
                        best = n
                        bestgoal = newgoal
                        bestmisfit = newmisfit
                        bestcompactness = newcompactness
                if best is not None:
                    grew = True
                    goal = bestgoal
                    misfit = bestmisfit
                    compactness = bestcompactness
                    p[best.i] = best.prop
                    added.add(best.i)
                    neighbors[s].remove(best)
                    allneighbors.remove(best)
                    tmp = best.neighbors.difference(allneighbors).difference(added)
                    neighbors[s].add(tmp)
                    allneighbors.add(tmp)
            if not grew:
                break
        self.p_ = p
        return self


class _Neighbor(object):
    """
    """

    def __init__(self, index, prop, mesh):
        self.index = index
        self.prop = prop
        self.mesh = mesh

    def __repr__(self):
        return str(self.index)

    def __eq__(self, other):
        "Compare if another neighbor (or an index in the mesh) is this one."
        if isinstance(other, int):
            return self.index == other
        elif hasattr(other, 'index'):
            return self.index == other.index
        else:
            raise ValueError("Can't compare Neighbor object to {} type".format(
                str(type(other))))

    def __hash__(self):
        "A unique value identifying this neighbor (it's index in the mesh)"
        return self.index

    @property
    def neighbors(self):
        "Find the neighboring prisms in the mesh."
        nz, ny, nx = self.mesh.shape
        n = self.index
        indexes = []
        # The guy above
        tmp = n - nx*ny
        if tmp > 0:
            indexes.append(tmp)
        # The guy below
        tmp = n + nx*ny
        if tmp < self.mesh.size:
            indexes.append(tmp)
        # The guy in front
        tmp = n + 1
        if n % nx < nx - 1:
            indexes.append(tmp)
        # The guy in the back
        tmp = n - 1
        if n % nx != 0:
            indexes.append(tmp)
        # The guy to the left
        tmp = n + nx
        if n % (nx*ny) < nx*(ny - 1):
            indexes.append(tmp)
        # The guy to the right
        tmp = n - nx
        if n % (nx*ny) >= nx:
            indexes.append(tmp)
        # Filter out the ones that are masked (topography)
        return set([_Neighbor(i, self.prop, self.mesh)
                    for i in indexes if self.mesh[i] is not None])


def _sow(seeds, mesh):
    pass