from .. import App, Vec3
from .fpo import print_err
import Part
from importlib import reload
from . import interpolation


class SeamProfile:
    def __init__(self, contour):
        self.contour = contour
        self.seam = self.get_shape()
        self.top_gutter_width = 10.0
        self.top_gutter_depth = 0.2
        self.bottom_gutter_width = 30.0
        self.bottom_gutter_depth = 1.5
        self.apex_height = 20
        self.apex_pos = 0.6
        self.apex_strength = 1.5

    def get_top_edge(self, param):
        """
        Return the top edge between between 0.0 and param
        """
        c1 = self.seam.Edge1.Curve
        c1.segment(0.0, param)
        return c1.toShape()

    def get_middle_edge(self, par1, par2):
        """
        Return the middle edge between between par1 and par2
        """
        c1 = self.seam.Edge1.Curve
        c1.segment(par1, par2)
        return c1.toShape()

    def get_bottom_edge(self, param):
        """
        Return the bottom edge between between param and 100.0
        """
        c1 = self.seam.Edge1.Curve
        c1.segment(param, 100.0)
        return c1.toShape()

    def get_shape(self, flat=False):
        top = self.contour.Vertex1.Point
        bottom = self.contour.Vertexes[-1].Point
        height = top.distanceToPoint(bottom)
        if top.y < bottom.y:
            top, bottom = bottom, top
        pts = [top]
        pts.append(top - Vec3(0.0, self.top_gutter_width / 2.0, self.top_gutter_depth))
        pts.append(top - Vec3(0.0, self.top_gutter_width, 0.0))
        pts.append(top + Vec3(0.0, -height * self.apex_pos, self.apex_height))
        # pts.append(bottom + Vec3(0.0, self.bottom_gutter_width, 0.0))
        # pts.append(bottom + Vec3(0.0, self.bottom_gutter_width / 2.0, -self.bottom_gutter_depth))
        # pts.append(bottom)
        # tan = [bottom - top] * len(pts)
        # flags = [False, True, False, True, False, True, False]
        tan = bottom - top
        tan.normalize()
        pars = [-p.y for p in pts]
        # bs = Part.BSplineCurve()
        # try:
        #     bs.interpolate(Points=pts, Parameters=pars, Tangents=tan, TangentFlags=flags)
        #     bs.scaleKnotsToBounds(0.0, 100.0)
        # except Part.OCCError:
        #     print_err(pars)
        #     poly = Part.makePolygon(pts)
        #     return poly
        # self.bspline_tweak(bs)
        reload(interpolation)
        pi = interpolation.PointInterpolation(pts)
        pi.Parameters = pars  # + [300]
        pi.Derivatives = [None, tan, None, tan * self.apex_strength]
        bs1 = pi.interpolate(3)
        if flat:
            bs1.increaseMultiplicity(3, 3)
            pl = Part.Plane(top, Vec3(0, 0, 1))
            for i in range(5):
                p = bs1.getPole(i + 1)
                np = pl.projectPoint(p)
                bs1.setPole(i + 1, np)

        pts = []
        pts.append(top + Vec3(0.0, -height * self.apex_pos, self.apex_height))
        pts.append(bottom + Vec3(0.0, self.bottom_gutter_width, 0.0))
        pts.append(bottom + Vec3(0.0, self.bottom_gutter_width / 2.0, -self.bottom_gutter_depth))
        pts.append(bottom)
        pars = [-p.y for p in pts]
        pi = interpolation.PointInterpolation(pts)
        pi.Parameters = pars  # + [300]
        pi.Derivatives = [tan * self.apex_strength, None, tan, None]
        bs2 = pi.interpolate(3)
        if flat:
            bs2.increaseMultiplicity(2, 3)
            pl = Part.Plane(top, Vec3(0, 0, 1))
            for i in range(4, bs2.NbPoles):
                p = bs2.getPole(i + 1)
                np = pl.projectPoint(p)
                bs2.setPole(i + 1, np)
        bs1.join(bs2)
        bs1.scaleKnotsToBounds(0.0, 100.0)
        self.seam = bs1.toShape()
        return self.seam

