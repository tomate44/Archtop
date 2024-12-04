# -*- coding: utf-8 -*-

__title__ = "Seam Profile"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Seam profile of the archtop plate"
__usage__ = "Select the body contour and activate the tool."


# import FreeCADGui as Gui
import Part
from .. import os, Icon_Path
from ..lib.fpo import print_err, proxy, view_proxy, PropertyLink, PropertyLength

TOOL_ICON = os.path.join(Icon_Path, "Archtop_SeamProfile.svg")


@view_proxy(icon=TOOL_ICON)
class SeamProfileViewProxy:
    pass


@proxy(object_type="Part::FeaturePython", view_proxy=SeamProfileViewProxy)
class SeamProfileProxy:
    Contour = PropertyLink(section="Source",
                           default=None,
                           description="Object that define the contour")
    Gutter_Width = PropertyLength(section="SeamProfile",
                                  default=30,
                                  description="Width of the gutter")
    Gutter_Depth = PropertyLength(section="SeamProfile",
                                  default=2,
                                  description="Depth of the gutter")

    # Ensure execution by the first time
    def on_create(self, obj):
        pass  # self.on_execute(obj)

    def on_change(self, fpo, prop, new_value, old_value):
        if prop == "Contour":
            self.on_execute(fpo)

    def on_execute(self, obj):
        obj.Shape = Part.Shape()
