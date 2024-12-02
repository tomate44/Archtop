# -*- coding: utf-8 -*-

__title__ = "Profile 1"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = ""
__usage__ = ""

import os
import FreeCAD
import FreeCADGui
import Part
from freecad.Archtop import ICONPATH

TOOL_ICON = os.path.join(ICONPATH, 'icon.svg')


from freecad.Archtop.lib.fpo import proxy, PropertyLength, print_log

