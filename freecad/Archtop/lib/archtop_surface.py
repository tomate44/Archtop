from .. import App, Vec3, Tol3D
from .fpo import print_err
import Part
from freecad.Curves.gordon import InterpolateCurveNetwork
from . import curves_to_surface as CTS
from . import (contour,
               SweepPath)


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

    def get_contour_params(self, profiles):
        params = [prof.contour_param for prof in profiles]
        return params

    def top_rot_sweep(self):
        minpar, _ = self.get_seam_params()
        rot_prof = [pro for pro in self.profiles if abs(pro.seam_param - minpar) < Tol3D]
        seam_prof = self.seam.Edge1.Curve
        seam_prof.segment(0.0, minpar)
        seam_prof = seam_prof.toShape()
        rot_prof.sort(key=lambda x: x.contour_param)
        contour_param = rot_prof[-1].contour_param
        path = self.contour.get_top_edge(contour_param, contour_param)
        profiles = [prof.get_shape() for prof in rot_prof]
        profiles.append(seam_prof)
        rs = SweepPath.RotationSweep(path, profiles, True)
        rs.set_curves()
        return rs.Face

    def bottom_rot_sweep(self):
        _, maxpar = self.get_seam_params()
        rot_prof = [pro for pro in self.profiles if abs(pro.seam_param - maxpar) < Tol3D]
        print(len(rot_prof))
        seam_prof = self.seam.Edge1.Curve
        seam_prof.segment(maxpar, 100.0)
        seam_prof = seam_prof.toShape()
        rot_prof.sort(key=lambda x: x.contour_param)
        contour_param = rot_prof[0].contour_param
        path = self.contour.get_bottom_edge(contour_param, contour_param)
        profiles = [prof.get_shape() for prof in rot_prof]
        profiles.append(seam_prof)
        rs = SweepPath.RotationSweep(path, profiles, True)
        rs.set_curves()
        return rs.Face

    def corner_params(self):
        left, right = [], []
        for prof in self.profiles:
            if prof.contour.CenterOfGravity.x < 0:
                left.append(prof.contour_param)
            else:
                right.append(prof.contour_param)
        return min(right), max(right), min(left), max(left)

    def flat_gordon(self, *args):
        if len(args) == 0:
            corners = self.corner_params()
        elif len(args) == 2:
            corners = args * 2
        else:
            corners = args[:4]
        bounds = [e.Curve for e in self.contour.get_4_boundaries(*corners)]
        prof = bounds[:2]
        rails = bounds[2:]
        gordon = CTS.CurvesOn2Rails(prof, rails)
        return gordon.build_surface()

    def flat_profiles(self, gordon, num=5):
        minpar, maxpar = self.get_seam_params()
        minpt = self.seam.Edge1.valueAt(minpar)
        maxpt = self.seam.Edge1.valueAt(maxpar)
        minpar = gordon.parameter(minpt)[1]
        maxpar = gordon.parameter(maxpt)[1]
        top_curves = []
        bottom_curves = []
        for i in range(1, num + 1):
            par1 = i * minpar / (num + 1)
            top_curves.append(gordon.vIso(par1))
            par2 = maxpar + i * (1.0 - maxpar) / (num + 1)
            bottom_curves.append(gordon.vIso(par2))
        return top_curves, bottom_curves

    def extra_profiles(self, face, curves, num=100):
        surf = face.Surface
        line = Part.Line()
        curves3d = []
        for c in curves:
            pts = [c.value(c.FirstParameter)]
            samp = c.discretize(num)[1:-1]
            for pt in samp:
                line.Location = pt
                inter = surf.intersect(line)[0][0]
                pts.append(inter.toShape().Point)
            pts.append(c.value(c.LastParameter))
            bs = Part.BSplineCurve()
            bs.approximate(Points=pts, DegMin=3, DegMax=3, Tolerance=1e-3)
            curves3d.append(bs)
        return curves3d

    def inner_profiles(self):
        minpar, maxpar = self.get_seam_params()
        profs = []
        for prof in self.profiles:
            if ((prof.seam_param - minpar) > Tol3D) and ((maxpar - prof.seam_param) > Tol3D):
                profs.append((prof.seam_param, prof.get_shape().Curve))
        profs.sort(key=lambda x:x[0])
        print(profs)
        curves = []
        for i in range(0, len(profs), 2):
            c1 = profs[i][1]
            c2 = profs[i + 1][1]
            if c1.value(c1.LastParameter).x > 0.0:
                c1, c2 = c2, c1
            c1.reverse()
            c1.join(c2)
            curves.append(c1)
        return curves

    def get_shape(self):
        # Top and bottom Rotation Sweep faces
        rs1 = self.top_rot_sweep()
        rs2 = self.bottom_rot_sweep()
        # Flat gordon face
        gordon = self.flat_gordon()
        # Flat extra profiles generated on flat gordon
        top, bot = self.flat_profiles(gordon)
        # Extra profiles projected on RotationSweep surfaces
        top_profiles = self.extra_profiles(rs1, top)
        bot_profiles = self.extra_profiles(rs2, bot)
        # Extract inner profiles
        inner = self.inner_profiles()
        print("Inner profiles")
        print(inner)
        # Final Gordon surface curves
        profiles = [gordon.vIso(0.0)]
        profiles.extend(top_profiles)
        profiles.extend(inner)
        profiles.extend(bot_profiles)
        profiles.append(gordon.vIso(1.0))
        rails = [gordon.uIso(0.0), self.seam.Curve, gordon.uIso(1.0)]
        # Final Gordon surface
        final = InterpolateCurveNetwork(profiles, rails, 1e-2, 1e-3)
        final.max_ctrl_pts = 40
        # s = final.surface()
        # Debug shapes
        sh = final.surface().toShape()
        top_edges = [c.toShape() for c in top_profiles]
        bot_edges = [c.toShape() for c in bot_profiles]
        comp = Part.Compound([rs1, rs2, gordon] + top_edges + bot_edges + [sh])
        # Return shape
        return sh
