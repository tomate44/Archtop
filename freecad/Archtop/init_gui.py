import os
import FreeCADGui as Gui
from . import ICONPATH


class ArchtopWorkbench(Gui.Workbench):
    """
    FreeCAD workbench for modelling archtop guitar top and back plates
    """
    MenuText = "Archtop"
    ToolTip = "FreeCAD workbench for modelling archtop guitar top and back plates"
    Icon = os.path.join(ICONPATH, "icon.svg")
    toolbox = []

    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        # TODO changes module names to lower_with_underscore

        from . import lineFP

        curvelist = ["Curves_line"]
        surflist = []
        misclist = []

        self.appendToolbar("Curves", curvelist)
        self.appendToolbar("Surfaces", surflist)
        self.appendToolbar("Misc.", misclist)
        self.appendMenu("Curves", curvelist)
        self.appendMenu("Surfaces", surflist)
        self.appendMenu("Misc.", misclist)

    def Activated(self):
        """This function is executed when the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed when the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This is executed whenever the user right-clicks on screen.
        recipient" will be either 'view' or 'tree'"""
        # if recipient == "View":
        #     contextlist = ["Curves_adjacent_faces", "Curves_bspline_to_console"]  # list of commands
        #     self.appendContextMenu("Curves", contextlist)
        # elif recipient == "Tree":
        #     contextlist = []  # list of commands
        #     self.appendContextMenu("Curves", contextlist)
        return

    def GetClassName(self):
        """This function is mandatory if this is a full python workbench"""
        return "Gui::PythonWorkbench"


Gui.addWorkbench(ArchtopWorkbench())
