from .. import App, Vec3
from .fpo import print_err
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

    def get_shape(self):
        x_pt = self.contour.valueAt(self.contour_param)
        if self.seam_param is None:
            pl = Part.Plane(x_pt, Vec3(0, 1, 0))
            y_pt = pl.intersect(self.seam.Edge1.Curve)[0][0].toShape().Point
            par = self.seam.Edge1.Curve.parameter(y_pt)
            norm = self.seam.Edge1.normalAt(par)
        else:
            y_pt = self.seam.Edge1.valueAt(self.seam_param)
            norm = self.seam.Edge1.normalAt(self.seam_param)
        cs = ProfileCS(x_pt, y_pt, norm)
        print(cs)
        if not cs.isValid():
            return Part.Shape()
        bs = self.get_profile(cs)
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

    def get_profile(self, cs):
        print(cs.x_vec)
        x = Vec3(cs.x_vec)
        x.normalize()
        gutter_vec = x * self.gutter_width
        pts = [cs.y_pt]
        proj = cs.tangent_plane.projectPoint(cs.y_pt + cs.x_vec)
        start_tan = proj - cs.y_pt
        pts.append(cs.x_pt - gutter_vec)
        pts.append(cs.x_pt - gutter_vec / 2 - Vec3(0, 0, self.gutter_depth))
        pts.append(cs.x_pt)
        tan = [start_tan, Vec3(), x, Vec3()]
        flags = [True, False, True, False]
        line = Part.Line()
        line.Location = cs.origin
        line.Direction = x
        pars = [line.parameter(p) for p in pts]
        # pars = [pow(p, 1.5) for p in pars]
#		if pars[1] < pars[0]:
#			pars = pars[::-1]
        print(pars)
        bs = Part.BSplineCurve()
        bs.interpolate(Points=pts, Parameters=pars, Tangents=tan, TangentFlags=flags)
        return bs
