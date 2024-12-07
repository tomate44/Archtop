from .. import App, Vec3
from .fpo import print_err
import Part


class SeamProfile:
    def __init__(self, contour):
        self.contour = contour
        self.top_gutter_width = 10.0
        self.top_gutter_depth = 0.2
        self.bottom_gutter_width = 30.0
        self.bottom_gutter_depth = 1.5
        self.apex_height = 20
        self.apex_pos = 0.6
        self.apex_strength = 1.5

    def bspline_tweak(self, bs):
        pts = bs.getPoles()
        p1, p2, p3, p4 = pts[6:2:-1]
        p12 = p2 - p1
        p34 = p3 - p4
        bs.setPole(6, p1 + p12 * self.apex_strength)
        bs.setPole(5, p4 + p34 / self.apex_strength)
        return bs

    def get_shape(self, tweak=0.0):
        top = self.contour.Vertex1.Point
        bottom = self.contour.Vertexes[-1].Point
        height = top.distanceToPoint(bottom)
        if top.y < bottom.y:
            top, bottom = bottom, top
        pts = [top]
        pts.append(top - Vec3(0.0, self.top_gutter_width / 2.0, self.top_gutter_depth))
        pts.append(top - Vec3(0.0, self.top_gutter_width, 0.0))
        pts.append(top + Vec3(0.0, -height * self.apex_pos, self.apex_height))
        pts.append(bottom + Vec3(0.0, self.bottom_gutter_width, 0.0))
        pts.append(bottom + Vec3(0.0, self.bottom_gutter_width / 2.0, -self.bottom_gutter_depth))
        pts.append(bottom)
        tan = [bottom - top] * len(pts)
        flags = [False, True, False, True, False, True, False]
        pars = [-p.y for p in pts]
        bs = Part.BSplineCurve()
        try:
            bs.interpolate(Points=pts, Parameters=pars, Tangents=tan, TangentFlags=flags)
        except Part.OCCError:
            print_err(pars)
            poly = Part.makePolygon(pts)
            return poly
        self.bspline_tweak(bs)
        return bs.toShape()

