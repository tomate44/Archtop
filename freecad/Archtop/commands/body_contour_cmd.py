# -*- coding: utf-8 -*-

__title__ = "Body Contour"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Contour of the archtop plate"
__usage__ = "Select the body contour and activate the tool."


import FreeCADGui as Gui
from .. import os, App, Icon_Path
from ..feature_python_objects import contour_fpo as feat
from ..lib.fpo import print_err


TOOL_ICON = os.path.join(Icon_Path, "Archtop_BodyContour.svg")


class CmdBodyContour:
    "Body Contour Command"

    Name = 'Archtop_BodyContour'

    def makeFeature(self, source):
        featname = 'Contour'
        fp = feat.ContourProxy.create(name=featname, label=featname)
        fp.Source = source

    def Activated(self):
        sel = Gui.Selection.getSelection()
        if sel:
            self.makeFeature(sel)
        else:
            print_err("Select body contour edges first.")

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
