# -*- coding: utf-8 -*-

__title__ = "Profile 1"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = ""
__usage__ = ""

import FreeCADGui as Gui
from .. import os, App, Icon_Path
from ..lib.fpo import proxy, view_proxy

TOOL_ICON = os.path.join(Icon_Path, "Archtop_CrossProfile.svg")

@view_proxy(icon=TOOL_ICON)
class CrossProfileViewProxy:
    pass


@proxy(object_type="Part::FeaturePython", view_proxy=CrossProfileViewProxy)
class CrossProfileProxy:
    pass
