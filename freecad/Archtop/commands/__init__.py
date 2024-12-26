# -*- coding: utf-8 -*-

import FreeCADGui as Gui

# Import Commands
from .body_contour_cmd import CmdBodyContour
from .seam_profile_cmd import CmdSeamProfile
from .cross_profile_cmd import CmdCrossProfile
from .archtop_surface_cmd import CmdArchtopSurface

# Register Commands
Gui.addCommand(CmdBodyContour.Name, CmdBodyContour())
Gui.addCommand(CmdSeamProfile.Name, CmdSeamProfile())
Gui.addCommand(CmdCrossProfile.Name, CmdCrossProfile())
Gui.addCommand(CmdArchtopSurface.Name, CmdArchtopSurface())

Cmd_Names = [CmdBodyContour.Name,
             CmdSeamProfile.Name,
             CmdCrossProfile.Name,
             CmdArchtopSurface.Name]
