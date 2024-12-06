# -*- coding: utf-8 -*-

__title__ = "Cross Profile"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Cross profile of the archtop plate"
__usage__ = "Select the body contour + the seam and activate the tool."

import Part
from .. import os, Icon_Path, reload
from ..lib.fpo import (print_err,
                       proxy,
                       view_proxy,
                       PropertyLink,
                       PropertyLinkSub,
                       PropertyLength,
                       PropertyFloat,
                       PropertyBool)
from ..lib import cross_profile

TOOL_ICON = os.path.join(Icon_Path, "Archtop_CrossProfile.svg")

@view_proxy(icon=TOOL_ICON)
class CrossProfileViewProxy:
    pass


@proxy(object_type="Part::FeaturePython", view_proxy=CrossProfileViewProxy)
class CrossProfileProxy:
    Contour = PropertyLinkSub(section="Source",
                              default=None,
                              description="Snap Edge on the contour")
    Contour_Param = PropertyFloat(section="Source",
                                  default=0.0,
                                  description="Parameter on the contour")
    Seam = PropertyLink(section="Source",
                        default=None,
                        description="Object that define the Seam")
    Seam_Param = PropertyFloat(section="Source",
                               default=0.0,
                               description="Parameter on the seam")
    Binding_Size = PropertyLength(section="CrossProfile",
                                  default=3.0,
                                  description="Width of the binding")
    Horizontal = PropertyBool(section="CrossProfile",
                              default=True,
                              description="Force horizontal profile")
    Gutter_Width = PropertyLength(section="CrossProfile",
                                  default=30,
                                  description="Width of the gutter")
    Gutter_Depth = PropertyLength(section="CrossProfile",
                                  default=2,
                                  description="Depth of the gutter")
    Apex_Strength = PropertyFloat(section="CrossProfile",
                                  default=1.5,
                                  description="Strength of the apex point")

    # Ensure execution by the first time
    def on_create(self, obj):
        pass  # self.on_execute(obj)

    def on_change(self, fpo, prop, new_value, old_value):
        return
        if prop in ("Contour", "Seam"):
            self.on_execute(fpo)

    def on_execute(self, obj):
        print(obj.State)
        reload(cross_profile)
        contour = self.Contour[0].getSubObject(self.Contour[1])[0]
        print(contour)
        seam = self.Seam.Shape
        prof = cross_profile.CrossProfile(contour, seam)
        prof.contour_param = self.Contour_Param
        prof.seam_param = self.Seam_Param
        prof.gutter_width = self.Gutter_Width
        prof.gutter_depth = self.Gutter_Depth
        prof.apex_strength = self.Apex_Strength
        obj.Shape = prof.get_shape()
