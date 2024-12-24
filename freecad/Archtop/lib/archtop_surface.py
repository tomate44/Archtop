from .. import App, Vec3
from .fpo import print_err
import Part
from . import contour


def edge_in_list(edge, edges):
    "Check if edge is already in edges list"
    for e in edges:
        if edge.isSame(e):
            return True
    return False


class ArchtopSurface:
    """
    BSpline surface that skins a set of profiles
    defined between a contour and a seam
    """

    def __init__(self, profiles):
        self.profiles = profiles
        self.seam = profiles[0].seam
        edges = []
        for prof in profiles:
            if not edge_in_list(prof.contour, edges):
                edges.append(prof.contour)
        self.contour = contour.Contour(edges)

    def get_seam_params(self):
        params = [prof.seam_param for prof in self.profiles]
        return min(params), max(params)

