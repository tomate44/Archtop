# -*- coding: utf-8 -*-

__title__ = "Cross Profile"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Cross profile of the archtop plate"
__usage__ = "Select the body contour, the seam profile and activate the tool."


import FreeCADGui as Gui
from .. import os, App, Icon_Path


TOOL_ICON = os.path.join(Icon_Path, "Archtop_CrossProfile.svg")


class CmdCrossProfile:
    "Cross profile Command"

    Name = 'Archtop_CrossProfile'

    def makeFeature(self, source):
        pass

    def Activated(self):
        sel = Gui.Selection.getSelection()
        print(sel)

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
