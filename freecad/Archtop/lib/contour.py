from .. import App, Vec3
from .fpo import print_err
import Part


class Contour:
    def __init__(self, shapes):
        self.contour = self.get_wire(shapes)
        self.gutter_width = 30.0
        self.gutter_depth = 2.0

    def get_wire(self, shapes):
        """
        Return a wire made of 2 edges
        First edge is the left side
        Second edge is the right side
        The 2 curves start at the top point
        """
        if isinstance(shapes, Part.Wire):
            return shapes
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

    def get_top_edge(self, left, right):
        """
        Return the top edge between :
        - left param on left half
        - right param on right half
        """
        c1 = self.contour.Edge1.Curve
        c1.segment(0.0, left)
        c1.reverse()
        c2 = self.contour.Edge2.Curve
        c2.segment(0.0, right)
        c1.join(c2)
        return c1.toShape()

    def get_bottom_edge(self, left, right):
        """
        Return the bottom edge between :
        - left param on left half
        - right param on right half
        """
        c1 = self.contour.Edge1.Curve
        c1.segment(left, 100.0)
        c2 = self.contour.Edge2.Curve
        c2.segment(right, 100.0)
        c2.reverse()
        c1.join(c2)
        return c1.toShape()

    def get_left_edge(self, top, bottom):
        """
        Return the left edge segment between
        top param and bottom param
        """
        c1 = self.contour.Edge1.Curve
        c1.segment(top, bottom)
        return c1.toShape()

    def get_right_edge(self, top, bottom):
        """
        Return the right edge segment between
        top param and bottom param
        """
        c1 = self.contour.Edge2.Curve
        c1.segment(top, bottom)
        return c1.toShape()

    def get_4_boundaries(self, topright, bottomright, topleft, bottomleft):
        """
        Return the 4 boundary edges of the contour
        split at the supplied parameters
        Return list is [top, bottom, left, right]
        """
        top = self.get_top_edge(topleft, topright)
        bottom = self.get_bottom_edge(bottomleft, bottomright)
        left = self.get_left_edge(topleft, bottomleft)
        right = self.get_right_edge(topright, bottomright)
        return [top, bottom, left, right]
