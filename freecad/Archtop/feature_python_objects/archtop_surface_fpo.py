# -*- coding: utf-8 -*-

__title__ = "Archtop Surface"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Generate the archtop surface"
__usage__ = "Select the profile objects and activate the tool."


# import FreeCADGui as Gui
from importlib import reload
import Part
from .. import os, Icon_Path
from ..lib.fpo import (print_err,
                       proxy,
                       view_proxy,
                       PropertyLinkList,
                       PropertyLength,
                       PropertyBool)
from ..lib import archtop_surface

TOOL_ICON = os.path.join(Icon_Path, "Archtop_Surface.svg")


@view_proxy(icon=TOOL_ICON)
class ArchtopSurfaceViewProxy:

    def on_attach(self, vp):
        pass  # self.children_visi = None

    # def on_object_change(self, fp, prop):
    #     if prop == "Source":
    #         self.children_visi = []
    #         for o in fp.Source:
    #             self.children_visi.append(o.ViewObject.Visibility)
    #
    # def on_claim_children(self):
    #     for o in self.Object.Source:
    #         o.ViewObject.Visibility = False
    #     return self.Object.Source
    #
    # def on_delete(self, vp, subelements):
    #     for i, o in enumerate(self.Object.Source):
    #         o.ViewObject.Visibility = self.children_visi[i]
    #     return True


@proxy(object_type="Part::FeaturePython", view_proxy=ArchtopSurfaceViewProxy)
class ArchtopSurfaceProxy:
    Profiles = PropertyLinkList(section="Source",
                                description="Profiles of the archtop surface")
    # Binding_Size = PropertyLength(section="Contour",
    #                               default=3.0,
    #                               description="Width of the binding")
    # Gutter_Width = PropertyLength(section="Contour",
    #                               default=30.0,
    #                               description="Global width of the gutter")
    # Gutter_Depth = PropertyLength(section="Contour",
    #                               default=2.0,
    #                               description="Global depth of the gutter")
    # Flat_Gutter = PropertyBool(section="Contour",
    #                            default=False,
    #                            description="Flatten the gutter")

    # Ensure execution by the first time
    def on_create(self, obj):
        pass  # self.on_execute(obj)

    # def on_change(self, fpo, prop, new_value, old_value):
    #     if prop == "Source":
    #         self.on_execute(fpo)
    #
    def get_surface(self, obj):
        if not obj.Profiles:
            return
        objs = []
        for o in self.Profiles:
            objs.append(o.Proxy.get_cross_profile())
        reload(archtop_surface)
        surf = archtop_surface.ArchtopSurface(objs)
        return surf

    # Update the shape
    def on_execute(self, obj):
        surf = self.get_surface(obj)
        obj.Shape = surf.get_shape()  # contour.contour
