import os
import FreeCAD as App
from importlib import reload

WB_Path = os.path.dirname(__file__)
Icon_Path = os.path.join(WB_Path, "resources", "icons")

Tol3D = 1e-7
Tol2D = 1e-9
if hasattr(App.Base, "Precision"):
    Tol3D = App.Base.Precision.confusion()
    Tol2D = App.Base.Precision.parametric(Tol3D)

Vec3 = App.Vector
Vec2 = App.Base.Vector2d
