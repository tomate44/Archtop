import os
import FreeCADGui as Gui
from . import Icon_Path


class ArchtopWorkbench(Gui.Workbench):
    """
    FreeCAD workbench for modelling archtop guitar top and back plates
    """
    MenuText = "Archtop"
    ToolTip = "FreeCAD workbench for modelling archtop guitar top and back plates"
    Icon = os.path.join(Icon_Path, "Archtop_WorkBench.svg")
    toolbox = []

    def Initialize(self):
        """This function is executed when FreeCAD starts"""

        from . import commands

        self.appendToolbar("Archtop", commands.Cmd_Names)
        self.appendMenu("Archtop", commands.Cmd_Names)

    def Activated(self):
        """This function is executed when the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed when the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This is executed whenever the user right-clicks on screen.
        recipient" will be either 'view' or 'tree'"""
        return

    def GetClassName(self):
        """This function is mandatory if this is a full python workbench"""
        return "Gui::PythonWorkbench"


Gui.addWorkbench(ArchtopWorkbench())
