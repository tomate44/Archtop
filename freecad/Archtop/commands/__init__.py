# -*- coding: utf-8 -*-

from freecad.Archtop.fc import Gui

# Import Commands
from .body_contour_cmd import CmdBodyContour
from .seam_profile_cmd import CmdSeamProfile
from .cross_profile_cmd import CmdCrossProfile

# Register Commands
Gui.addCommand('ArchtopBodyContour', CmdBodyContour())
Gui.addCommand('ArchtopSeamProfile', CmdSeamProfile())
Gui.addCommand('ArchtopCrossProfile', CmdCrossProfile())
