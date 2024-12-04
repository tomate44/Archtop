# -*- coding: utf-8 -*-

__title__ = "Seam Profile"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Seam profile of the archtop plate"
__usage__ = "Select the body contour and activate the tool."


import FreeCADGui as Gui
from .. import os, App, Icon_Path
from ..feature_python_objects import seam_profile_fpo as feat
from ..lib.fpo import print_err


TOOL_ICON = os.path.join(Icon_Path, "Archtop_SeamProfile.svg")


class CmdSeamProfile:
    "Seam profile Command"

    Name = 'Archtop_SeamProfile'

    def makeFeature(self, source):
        fp = feat.SeamProfileProxy.create(label='Seam Profile')
        fp.Contour = source

    def Activated(self):
        sel = Gui.Selection.getSelection()
        if sel:
            self.makeFeature(sel[0])
        else:
            print_err("Select an Archtop body contour object first.")

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

    def GetResources(self):
        usage = "<br>".join(__usage__.splitlines())
        return {'Pixmap': TOOL_ICON,
                'MenuText': __title__,
                'ToolTip': f"{__doc__}<br><br><b>Usage :</b><br>{usage}"}