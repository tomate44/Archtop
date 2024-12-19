# -*- coding: utf-8 -*-

__title__ = "Contour"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Contour of the archtop plate"
__usage__ = "Select the body contour edges and activate the tool."


# import FreeCADGui as Gui
from importlib import reload
import Part
from .. import os, Icon_Path
from ..lib.fpo import (print_err,
                       proxy,
                       view_proxy,
                       PropertyLinkList,
                       PropertyLength)
from ..lib import contour

TOOL_ICON = os.path.join(Icon_Path, "Archtop_BodyContour.svg")


@view_proxy(icon=TOOL_ICON)
class ContourViewProxy:

    def on_attach(self, vp):
        self.children_visi = None

    def on_object_change(self, fp, prop):
        if prop == "Source":
            self.children_visi = []
            for o in fp.Source:
                self.children_visi.append(o.ViewObject.Visibility)

    def on_claim_children(self):
        for o in self.Object.Source:
            o.ViewObject.Visibility = False
        return self.Object.Source

    def on_delete(self, vp, subelements):
        for i, o in enumerate(self.Object.Source):
            o.ViewObject.Visibility = self.children_visi[i]
        return True


@proxy(object_type="Part::FeaturePython", view_proxy=ContourViewProxy)
class ContourProxy:
    Source = PropertyLinkList(section="Source",
                              description="Objects that define the contour")
    Binding_Size = PropertyLength(section="Contour",
                                  default=3.0,
                                  description="Width of the binding")
    Gutter_Width = PropertyLength(section="Contour",
                                  default=30.0,
                                  description="Global width of the gutter")
    Gutter_Depth = PropertyLength(section="Contour",
                                  default=2.0,
                                  description="Global depth of the gutter")

    # Ensure execution by the first time
    def on_create(self, obj):
        pass  # self.on_execute(obj)

    def on_change(self, fpo, prop, new_value, old_value):
        if prop == "Source":
            self.on_execute(fpo)

    def get_contour_wire(self, obj):
        if not obj.Source:
            return
        shapes = []
        for o in self.Source:
            shapes.append(o.Shape)
        reload(contour)
        body = contour.Contour(shapes)
        return body.contour
        # sorted_edges = Part.sortEdges(edges)
        # if len(sorted_edges) > 1:
        #     print_err("Edges don't form a closed contour")
        #     return Part.Shape()
        # wire = Part.Wire(sorted_edges[0])
        # if not wire.isClosed():
        #     print_err("Edges don't form a closed contour")
        # return wire

    # Update the shape
    def on_execute(self, obj):
        obj.Shape = self.get_contour_wire(obj)
