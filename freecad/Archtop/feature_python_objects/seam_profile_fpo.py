# -*- coding: utf-8 -*-

__title__ = "Seam Profile"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Seam profile of the archtop plate"
__usage__ = "Select the body contour and activate the tool."


# import FreeCADGui as Gui
import Part
from .. import os, Icon_Path, reload
from ..lib.fpo import (print_err,
                       proxy,
                       view_proxy,
                       PropertyLink,
                       PropertyLength,
                       PropertyFloat)
from ..lib import seam_profile

TOOL_ICON = os.path.join(Icon_Path, "Archtop_SeamProfile.svg")


@view_proxy(icon=TOOL_ICON)
class SeamProfileViewProxy:
    pass


@proxy(object_type="Part::FeaturePython", view_proxy=SeamProfileViewProxy)
class SeamProfileProxy:
    Contour = PropertyLink(section="Source",
                           default=None,
                           description="Object that define the contour")
    Binding_Size = PropertyLength(section="SeamProfile",
                                  default=3.0,
                                  description="Width of the binding")
    Top_Gutter_Width = PropertyLength(section="SeamProfile",
                                      default=30,
                                      description="Width of the gutter at top end")
    Top_Gutter_Depth = PropertyLength(section="SeamProfile",
                                      default=2,
                                      description="Depth of the gutter at top end")
    Bottom_Gutter_Width = PropertyLength(section="SeamProfile",
                                         default=30,
                                         description="Width of the gutter at bottom end")
    Bottom_Gutter_Depth = PropertyLength(section="SeamProfile",
                                         default=2,
                                         description="Depth of the gutter at bottom end")
    Apex_Position = PropertyFloat(section="SeamProfile",
                                  default=0.6,
                                  description="Relative position of the arch apex along seam profile")
    Apex_Height = PropertyLength(section="SeamProfile",
                                 default=20,
                                 description="Height of the arch apex")
    Apex_Strength = PropertyFloat(section="SeamProfile",
                                  default=1.5,
                                  description="Strength of the apex point")

    # Ensure execution by the first time
    def on_create(self, obj):
        pass  # self.on_execute(obj)

    def on_change(self, fpo, prop, new_value, old_value):
        if prop == "Contour":
            self.on_execute(fpo)

    def on_execute(self, obj):
        if not obj.Contour:
            return
        reload(seam_profile)
        contour = self.Contour.Shape
        prof = seam_profile.SeamProfile(contour)
        prof.top_gutter_width = self.Top_Gutter_Width
        prof.top_gutter_depth = self.Top_Gutter_Depth
        prof.bottom_gutter_width = self.Bottom_Gutter_Width
        prof.bottom_gutter_depth = self.Bottom_Gutter_Depth
        prof.apex_height = self.Apex_Height
        prof.apex_pos = self.Apex_Position
        prof.apex_strength = self.Apex_Strength
        obj.Shape = prof.get_shape()

