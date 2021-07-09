import flask_admin as admin

# Models for CRUD views.
from models import db
from views.general import LogoutMenuLink, LoginMenuLink, UserModelView
from views.help import HelpView
from views.mesh import MeshView
from views.odkconfig import OdkconfigView
from views.odmconfig import OdmconfigView

from models.mesh import Mesh
from models.odk import Odk
from models.odm import Odm


admin = admin.Admin(name="3D Streetview", template_mode="bootstrap4", url="/dashboard", base_template="base.html")

# Login/logout menu links.
admin.add_link(LogoutMenuLink(name="Logout", category="", url="/logout"))
admin.add_link(LoginMenuLink(name="Login", category="", url="/login"))

# Publicly visible pages.
admin.add_view(OdkconfigView(session=db, model=Odk, name="ODK configuration", url="odkconfig", category="Servers"))
admin.add_view(OdmconfigView(session=db, model=Odm, name="ODM configuration", url="odmconfig", category="Servers"))
admin.add_view(MeshView(session=db, model=Mesh, name="Meshes", url="mesh"))
admin.add_view(HelpView(name="Help", url="help"))


