from .. import App, Vec3
from .fpo import print_err
from importlib import reload
from . import interpolation
import Part


class ProfileCS:
    def __init__(self, x, y, n):
        self.x_pt = x
        self.y_pt = y
        self.normal = n
        self.origin = Vec3(self.y_pt.x, self.y_pt.y, 0)  # line.projectPoint(self.x_pt)
        self.x_vec = self.x_pt - self.origin
        self.tangent_plane = Part.Plane(y, n)
        # self.tangent_plane.Position = y
        # self.tangent_plane.Axis = n
        # line = Part.Line()
        # line.Location = self.y_pt
        # line.Direction = self.normal

    def __repr__(self):
        def vec_repr(v):
            vals = [f"{val:.3f}" for val in v]
            return ", ".join(vals)
        vecs = [self.origin, self.x_pt, self.y_pt]
        return "ProfileCS\n" + "\n".join([vec_repr(v) for v in vecs])

    def isValid(self):
        return (self.x_vec.Length > 0) and (self.normal.Length > 0)


class CrossProfile:
    def __init__(self, contour, par1, seam, par2=None):
        self.contour = contour  # Edge
        self.seam = seam  # Shape
        self.contour_param = par1
        self.seam_param = par2
        self.gutter_width = 30.0
        self.gutter_depth = 1.5
        self.apex_strength = 1.5

    def get_contour_param(self):
        y_pt = self.seam.Edge1.Curve.value(self.seam_param)
        pl = Part.Plane(y_pt, Vec3(0, 1, 0))
        x_pt = pl.intersect(self.contour.Edge1.Curve)[0][0].toShape().Point
        return self.contour.Edge1.Curve.parameter(x_pt)

    def get_seam_param(self):
        x_pt = self.contour.Curve.value(self.contour_param)
        pl = Part.Plane(x_pt, Vec3(0, 1, 0))
        y_pt = pl.intersect(self.seam.Edge1.Curve)[0][0].toShape().Point
        return self.seam.Edge1.Curve.parameter(y_pt)

    def get_shape(self, flat=False):
        x_pt = self.contour.Curve.value(self.contour_param)
        if self.seam_param is None:
            self.seam_param = self.get_seam_param()
        y_pt = self.seam.Edge1.Curve.value(self.seam_param)
        norm = self.seam.Edge1.Curve.normal(self.seam_param)
        cs = ProfileCS(x_pt, y_pt, norm)
        print(cs)
        if not cs.isValid():
            return Part.Shape()
        bs = self.get_profile(cs)
        if flat:
            bs.increaseMultiplicity(2, 3)
            pl = Part.Plane(cs.origin, Vec3(0, 0, 1))
            for i in range(4, bs.NbPoles):
                p = bs.getPole(i + 1)
                np = pl.projectPoint(p)
                bs.setPole(i + 1, np)
        return bs.toShape()

    def get_profile(self, cs):
        off = self.contour.makeOffset2D(-self.gutter_width, 0, False, True , False)
        lineseg = Part.makeLine(cs.origin, cs.x_pt)
        dist, pts, info = lineseg.distToShape(off)
        gutter_vec = cs.x_pt - pts[0][0]
        x = Vec3(gutter_vec)
        x.normalize()
        # gutter_vec = x * self.gutter_width
        pts = [cs.y_pt]
        proj = cs.tangent_plane.projectPoint(cs.y_pt + cs.x_vec)
        start_tan = proj - cs.y_pt
        pts.append(cs.x_pt - gutter_vec)
        pts.append(cs.x_pt - gutter_vec / 2 - Vec3(0, 0, self.gutter_depth))
        pts.append(cs.x_pt)
        line = Part.Line()
        line.Location = cs.origin
        line.Direction = x
        pars = [line.parameter(p) for p in pts]
        print(pars)
        # tan = [start_tan, Vec3(), x, Vec3()]
        # flags = [True, False, True, False]
        # bs = Part.BSplineCurve()
        # bs.interpolate(Points=pts, Parameters=pars, Tangents=tan, TangentFlags=flags)
        reload(interpolation)
        pi = interpolation.PointInterpolation(pts)
        # pi.Periodic = True
        pi.Parameters = pars  # + [300]
        pi.Derivatives = [start_tan.normalize() * self.apex_strength, None, x.normalize(), None]
        bs = pi.interpolate(3)
        return bs
