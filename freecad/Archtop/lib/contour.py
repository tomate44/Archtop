from .. import App, Vec3
from .fpo import print_err
import Part


class Contour:
    def __init__(self, shapes):
        self.contour = self.get_wire(shapes)
        self.gutter_width = 30.0
        self.gutter_depth = 2.0

    def get_wire(self, shapes):
        if not len(shapes) == 2:
            raise ValueError("Two body halves are required")
        curves = []
        for sh in shapes:
            c = sh.Edge1.Curve.toBSpline()
            p1 = c.value(c.FirstParameter)
            p2 = c.value(c.LastParameter)
            if p1.y < p2.y:
                c.reverse()
                p1, p2 = p2, p1
            c.translate(-p1)
            c.scaleKnotsToBounds(0.0, 100.0)
            mid = c.value(50.0)
            if mid.x < 0.0:
                curves.insert(0, c)
            else:
                curves.append(c)
        e1 = curves[0].toShape()
        e2 = curves[1].toShape()
        e2.reverse()
        w = Part.Wire([e1, e2])
        return w
