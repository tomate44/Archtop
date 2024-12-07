from .. import App, Vec3
from .fpo import print_err
import Part


class CrossProfile:
    def __init__(self, contour, seam):
        self.contour = contour
        self.seam = seam
        self.contour_param = 0.5
        self.seam_param = 0.0
        self.gutter_width = 30.0
        self.gutter_depth = 1.5
        self.apex_strength = 1.5

    def get_shape(self):
        top = self.contour.Vertex1.Point
        bottom = self.contour.Vertexes[-1].Point
        height = top.distanceToPoint(bottom)
        if top.y < bottom.y:
            top, bottom = bottom, top
        axis = Part.makeLine(top, bottom)
        x = self.contour.valueAt(self.contour_param)
            # tan = self.seam
        if self.seam_param == 0.0:
            pl = Part.Plane(x, axis.Curve.Direction)
            y = pl.intersect(self.seam.Edge1.Curve)[0][0].toShape().Point
            o = pl.intersect(axis.Curve)[0][0].toShape().Point
        else:
            y = self.seam.valueAt(self.seam_param)
            n = self.seam.normalAt(self.seam_param)
            pl = Part.Plane(y, (n).cross(x - y))
            o = pl.intersect(axis.Curve)[0][0].toShape().Point
        print(o, x, y)
        bs = self.get_profile(o, x, y)
        self.bspline_tweak(bs)
        # return Part.makePolygon([x, o, y])
        return bs.toShape()

    def bspline_tweak(self, bs):
        pts = bs.getPoles()
        p1, p2, p3, p4 = pts[:4]
        p12 = p2 - p1
        p34 = p3 - p4
        bs.setPole(2, p1 + p12 * self.apex_strength)
        bs.setPole(3, p4 + p34 / self.apex_strength)
        return bs

    def get_profile(self, o, x, y):
        chord = x - o
        sign = 1
        if chord.x < 0:
            sign = -1
        gwidth = chord.Length
        pts = [y]
        pts.append(o + Vec3(chord.x - sign * self.gutter_width, 0.0, 0.0))
        pts.append(o + Vec3(chord.x - sign * self.gutter_width / 2, 0.0, -self.gutter_depth))
        pts.append(x)
        tan = [chord] * len(pts)
        flags = [True, False, True, False]
        pars = [sign * p.x for p in pts]
        # pars = [pow(p, 1.5) for p in pars]
#		if pars[1] < pars[0]:
#			pars = pars[::-1]
        print(pars)
        bs = Part.BSplineCurve()
        bs.interpolate(Points=pts, Parameters=pars, Tangents=tan, TangentFlags=flags)
        return bs
