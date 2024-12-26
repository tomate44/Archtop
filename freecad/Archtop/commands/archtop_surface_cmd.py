# -*- coding: utf-8 -*-

__title__ = "Archtop Surface"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Generate the archtop surface"
__usage__ = "Select the profile objects and activate the tool."


import FreeCADGui as Gui
from .. import os, App, Icon_Path
from ..feature_python_objects import archtop_surface_fpo as feat
from ..lib.fpo import print_err


TOOL_ICON = os.path.join(Icon_Path, "Archtop_Surface.svg")


class CmdArchtopSurface:
    "Archtop Surface Command"

    Name = 'Archtop_ArchtopSurface'

    def makeFeature(self, source):
        featname = 'ArchtopSurface'
        fp = feat.ArchtopSurfaceProxy.create(name=featname, label=featname)
        fp.Profiles = source

    def Activated(self):
        sel = Gui.Selection.getSelection()
        if sel:
            self.makeFeature(sel)
        else:
            print_err("Select profile objects first.")

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
