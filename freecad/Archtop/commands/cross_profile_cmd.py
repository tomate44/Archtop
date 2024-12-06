# -*- coding: utf-8 -*-

__title__ = "Cross Profile"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Cross profile of the archtop plate"
__usage__ = "Select the body contour, the seam profile and activate the tool."


import FreeCADGui as Gui
import Part
from .. import os, App, Icon_Path
from ..feature_python_objects import cross_profile_fpo as feat
from ..lib.fpo import print_err

TOOL_ICON = os.path.join(Icon_Path, "Archtop_CrossProfile.svg")


class CmdCrossProfile:
    "Cross profile Command"

    Name = 'Archtop_CrossProfile'

    def makeFeature(self):
        featname = 'Cross Profile'
        fp = feat.CrossProfileProxy.create(name=featname, label=featname)
        return fp

    def Activated(self):
        sel = Gui.Selection.getSelectionEx()
        if not len(sel) == 2:
            print_err("Select Contour and Seam first")
            return
        print(sel)
        fp = self.makeFeature()
        contour = sel[0].Object
        fp.Contour = [contour, sel[0].SubElementNames[0]]
        fp.Seam = sel[1].Object
        # print(dir(fp))
        if hasattr(contour, "BindingSize"):
            fp.setExpression('BindingSize', f'{contour.Name}.BindingSize')
        if hasattr(contour, "GutterWidth"):
            fp.setExpression('GutterWidth', f'{contour.Name}.GutterWidth')
        if hasattr(contour, "GutterDepth"):
            fp.setExpression('GutterDepth', f'{contour.Name}.GutterDepth')
        App.ActiveDocument.recompute()
        if sel[0].PickedPoints:
            v = Part.Vertex(sel[0].PickedPoints[0])
            dist, pts, info = sel[0].Object.Shape.distToShape(v)
            if info[0][0] == "Edge":
                fp.ContourParam = info[0][2]
        if sel[1].PickedPoints:
            v = Part.Vertex(sel[1].PickedPoints[0])
            dist, pts, info = sel[1].Object.Shape.distToShape(v)
            if info[0][0] == "Edge":
                fp.SeamParam = info[0][2]
                fp.Horizontal = False

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
