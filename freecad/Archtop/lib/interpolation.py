from .. import App, Vec3
from .fpo import print_err
import Part
import numpy as np


class BsplineBasis:
    """Computes basis functions of a bspline curve, and its derivatives"""

    def __init__(self):
        self.knots = [0.0, 0.0, 1.0, 1.0]
        self.degree = 1

    def find_span(self, u):
        """ Determine the knot span index.
        - input: parameter u (float)
        - output: the knot span index (int)
        Nurbs Book Algo A2.1 p.68
        """
        n = len(self.knots) - self.degree - 1
        if u == self.knots[n + 1]:
            return n - 1
        low = self.degree
        high = n + 1
        mid = int((low + high) / 2)
        while (u < self.knots[mid] or u >= self.knots[mid + 1]):
            if (u < self.knots[mid]):
                high = mid
            else:
                low = mid
            mid = int((low + high) / 2)
        return mid

    def basis_funs(self, i, u):
        """ Compute the nonvanishing basis functions.
        - input: start index i (int), parameter u (float)
        - output: basis functions values N (list of floats)
        Nurbs Book Algo A2.2 p.70
        """
        N = [0. for x in range(self.degree + 1)]
        N[0] = 1.0
        left = [0.0]
        right = [0.0]
        for j in range(1, self.degree + 1):
            left.append(u - self.knots[i + 1 - j])
            right.append(self.knots[i + j] - u)
            saved = 0.0
            for r in range(j):
                temp = N[r] / (right[r + 1] + left[j - r])
                N[r] = saved + right[r + 1] * temp
                saved = left[j - r] * temp
            N[j] = saved
        return N

    def ders_basis_funs(self, i, u, n):
        """ Compute nonzero basis functions and their derivatives.
        First section is A2.2 modified to store functions and knot differences.
        - input: start index i (int), parameter u (float), number of derivatives n (int)
        - output: basis functions and derivatives ders (array2d of floats)
        Nurbs Book Algo A2.3 p.72
        """
        ders = [[0.0 for x in range(self.degree + 1)] for y in range(n + 1)]
        ndu = [[1.0 for x in range(self.degree + 1)] for y in range(self.degree + 1)]
        ndu[0][0] = 1.0
        left = [0.0]
        right = [0.0]
        for j in range(1, self.degree + 1):
            left.append(u - self.knots[i + 1 - j])
            right.append(self.knots[i + j] - u)
            saved = 0.0
            for r in range(j):
                ndu[j][r] = right[r + 1] + left[j - r]
                temp = ndu[r][j - 1] / ndu[j][r]
                ndu[r][j] = saved + right[r + 1] * temp
                saved = left[j - r] * temp
            ndu[j][j] = saved

        for j in range(0, self.degree + 1):
            ders[0][j] = ndu[j][self.degree]
        for r in range(0, self.degree + 1):
            s1 = 0
            s2 = 1
            a = [[0.0 for x in range(self.degree + 1)] for y in range(2)]
            a[0][0] = 1.0
            for k in range(1, n + 1):
                d = 0.0
                rk = r - k
                pk = self.degree - k
                if r >= k:
                    a[s2][0] = a[s1][0] / ndu[pk + 1][rk]
                    d = a[s2][0] * ndu[rk][pk]
                if rk >= -1:
                    j1 = 1
                else:
                    j1 = -rk
                if (r - 1) <= pk:
                    j2 = k - 1
                else:
                    j2 = self.degree - r
                for j in range(j1, j2 + 1):
                    a[s2][j] = (a[s1][j] - a[s1][j - 1]) / ndu[pk + 1][rk + j]
                    d += a[s2][j] * ndu[rk + j][pk]
                if r <= pk:
                    a[s2][k] = -a[s1][k - 1] / ndu[pk + 1][r]
                    d += a[s2][k] * ndu[r][pk]
                ders[k][r] = d
                j = s1
                s1 = s2
                s2 = j
        r = self.degree
        for k in range(1, n + 1):
            for j in range(0, self.degree + 1):
                ders[k][j] *= r
            r *= (self.degree - k)
        return ders

    def evaluate(self, u, d):
        """ Compute the derivative d of the basis functions.
        - input: parameter u (float), derivative d (int)
        - output: derivative d of the basis functions (list of floats)
        """
        n = len(self.knots) - self.degree - 1
        f = [0.0 for x in range(n)]
        span = self.find_span(u)
        ders = self.ders_basis_funs(span, u, d)
        for i, val in enumerate(ders[d]):
            f[span - self.degree + i] = val
        return f


class PointInterpolation:
    def __init__(self, pts):
        self.Points = pts
        self.Periodic = False
        self.Derivatives = [None] * len(pts)
        self.Parameters = None

    @property
    def NbPoints(self):
        return len(self.Points)

    @property
    def NbDerivs(self):
        return len([d for d in self.Derivatives if d is not None])

    @property
    def NbPoles(self):
        if self.Periodic:
            return self.NbPoints + self.NbDerivs + 1
        return self.NbPoints + self.NbDerivs

    def get_parameters(self, fac=1):
        # Computes a knot Sequence for a set of points
        # fac (0-1) : parameterization factor
        # fac=0 -> Uniform / fac=0.5 -> Centripetal / fac=1.0 -> Chord-Length
        pts = self.Points[::]
        if self.Periodic and pts[0].distanceToPoint(pts[-1]) > 1e-7:
            pts.append(pts[0])
        params = [0]
        for i in range(1, len(pts)):
            p = pts[i] - pts[i - 1]
            if isinstance(p, Vec3):
                le = p.Length
            else:
                le = p.length()
            pl = pow(le, fac)
            params.append(params[-1] + pl)
        return params

    def get_flatknots(self, degree, knots, mults=None):
        if mults is not None:
            flatknots = []
            for i in range(len(knots)):
                flatknots += [knots[i]] * mults[i]
        else:
            flatknots = knots
        return flatknots

    def clamp_knots(self, degree, knots):
        flatknots = [knots[0]] * (degree + 1)
        flatknots += knots[1:-1]
        flatknots += [knots[-1]] * (degree + 1)
        return flatknots

    def compute_knots(self, degree):
        if self.Periodic:
            nb_knots = self.NbPoles
        else:
            nb_knots = self.NbPoles - 2
        print(f"Nb Knots : {nb_knots}")
        if nb_knots == len(self.Parameters):
            return self.clamp_knots(degree, self.Parameters)
        params = []
        ders = self.Parameters[::]
        if self.Periodic:
            ders += [self.Derivatives[0]]
        for i in range(len(self.Parameters)):
            params.append(self.Parameters[i])
            if ders[i] is not None:
                params.append(self.Parameters[i])
        nb_intervals = len(params) - 1
        step = nb_intervals / (nb_knots - 1)
        print(f"Params : {params}")
        print(f"Step : {step}")
        knots = []
        for i in range(nb_knots - 1):
            v = i * step
            idx = int(v)
            fv = v - idx
            par1 = params[idx]
            par2 = params[idx + 1]
            k = ((1 - fv) * par1) + (fv * par2)
            knots.append(k)
        knots.append(params[-1])
        if self.Periodic:
            return knots
        return self.clamp_knots(degree, knots)

    def check_knots(self, degree, flatknots):
        if self.Periodic:
            return self.NbPoles == sum(flatknots)
        print(f"\nPeriodic : {self.Periodic}")
        print(f"Nb Poles : {self.NbPoles}")
        print(f"Parameters : {self.Parameters}")
        print(f"Flat knots : {flatknots}")
        if self.NbPoles == (len(flatknots) - degree - 1):
            print("Flat knot sequence is valid")
            return True
        return False

    def interpolate(self, degree=3, knots=None, mults=None):
        if self.Parameters is None:
            self.Parameters = self.get_parameters(1.0)
        if knots is None:
            flatknots = self.compute_knots(degree)
        else:
            flatknots = self.get_flatknots(knots, mults)
        valid = self.check_knots(degree, flatknots)  # indent this line once compute_knots is working fine.
        if not valid:
            return

        # knots = self.Parameters
        # n = len(knots)
        # for i in range(len(self.Derivatives)):
        #     if n == (nb_inner_knots + 2):
        #         break
        #     if self.Derivatives[i] is not None:
        #         k = 0.5 * (self.Parameters[i] + self.Parameters[i + 1])
        #         knots.append(k)
        #         n += 1
        # # knots = self.Parameters  #  + add_knots
        # knots.sort()
        # flatknots = [knots[0]] * (degree + 1)
        # flatknots += knots[1:-1]
        # flatknots += [knots[-1]] * (degree + 1)
        # # print(flatknots)

        lhs = np.array([[0.] * (self.NbPoles) for i in range(self.NbPoles)])
        rhsx = np.array([0.] * self.NbPoles)
        rhsy = np.array([0.] * self.NbPoles)
        rhsz = np.array([0.] * self.NbPoles)

        bb = BsplineBasis()
        bb.knots = flatknots
        bb.degree = degree

        i = 0
        for idx in range(len(self.Points)):
            rhsx[i] = self.Points[idx].x
            rhsy[i] = self.Points[idx].y
            rhsz[i] = self.Points[idx].z
            bbeval = bb.evaluate(self.Parameters[idx], 0)
            # print(bbeval)
            lhs[i] = bbeval
            i += 1
            if self.Derivatives[idx] is not None:
                rhsx[i] = self.Derivatives[idx].x
                rhsy[i] = self.Derivatives[idx].y
                rhsz[i] = self.Derivatives[idx].z
                lhs[i] = bb.evaluate(self.Parameters[idx], 1)
                # print(lhs[i])
                i += 1

        try:
            cp_x = np.linalg.solve(lhs, rhsx)
            cp_y = np.linalg.solve(lhs, rhsy)
            cp_z = np.linalg.solve(lhs, rhsz)
        except np.linalg.LinAlgError:
            print_err("Numpy linalg solver failed\n")
            return None

        poles = [Vec3(cp_x[i], cp_y[i], cp_z[i]) for i in range(self.NbPoles)]
        result = Part.BSplineCurve()
        # debug("{} poles : {}".format(len(poles), poles))
        # debug("{} knots : {}".format(len(knots), knots))
        # debug("{} mults : {}".format(len(mults), mults))
        # debug("degree : {}".format(self.degree))
        # debug("conti : {}".format(self.C2Continuous))
        knots = list(set(flatknots))
        knots.sort()
        mults = [flatknots.count(k) for k in knots]
        print(mults)
        result.buildFromPolesMultsKnots(poles, mults, knots, self.Periodic, degree)
        return result
