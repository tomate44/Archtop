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
    Flat_Gutter = PropertyBool(section="CrossProfile",
                               default=False,
                               description="Flatten the gutter")

    # Ensure execution by the first time
    def on_create(self, obj):
        pass  # self.on_execute(obj)

    @Seam_Param.observer
    def listener_seam_param(self, fp, new_value, old_value):
        if fp.Horizontal is True:
            prof = self.get_cross_profile()
            self.Contour_Param = prof.get_contour_param()
        self.on_execute(fp)

    @Contour_Param.observer
    def listener_contour_param(self, fp, new_value, old_value):
        if fp.Horizontal is True:
            prof = self.get_cross_profile()
            self.Seam_Param = prof.get_seam_param()
        self.on_execute(fp)

    @Horizontal.observer
    def listener_horizontal(self, fp, new_value, old_value):
        if new_value is True:
            if 0.0 < self.Seam_Param < 100.0:
                fp.setEditorMode("ContourParam", 1)
                self.listener_seam_param(fp, self.Seam_Param, self.Seam_Param)
            elif 0.0 < self.Contour_Param < 100.0:
                fp.setEditorMode("SeamParam", 1)
                self.listener_contour_param(fp, self.Contour_Param, self.Contour_Param)
        else:
            fp.setEditorMode("ContourParam", 0)
            fp.setEditorMode("SeamParam", 0)

    def on_change(self, fpo, prop, new_value, old_value):
        if prop in ("Contour",
                    "Seam",
                    "Contour_Param",
                    "Seam_Param"):
            self.on_execute(fpo)

    def get_cross_profile(self):
        if not (self.Contour and self.Seam):
            return None
        reload(cross_profile)
        contour = self.Contour[0].getSubObject(self.Contour[1])[0]
        print(contour)
        par1 = self.Contour_Param
        par2 = self.Seam_Param
        seam = self.Seam.Shape
        if par2 == 0.0:
            par2 = None
        prof = cross_profile.CrossProfile(contour, par1, seam, par2)
        prof.gutter_width = self.Gutter_Width
        prof.gutter_depth = self.Gutter_Depth
        prof.apex_strength = self.Apex_Strength
        return prof

    def on_execute(self, obj):
        prof = self.get_cross_profile()
        if prof is None:
            return
        obj.Shape = prof.get_shape(self.Flat_Gutter)
