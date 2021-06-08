import flask_admin as admin

# Models for CRUD views.
from models import db
from views.general import LogoutMenuLink, LoginMenuLink, UserModelView
from views.help import HelpView
from views.mesh import MeshView
from models.mesh import Mesh

admin = admin.Admin(name="3D Streetview", template_mode="bootstrap4", url="/dashboard", base_template="base.html")

# Login/logout menu links.
admin.add_link(LogoutMenuLink(name="Logout", category="", url="/logout"))
admin.add_link(LoginMenuLink(name="Login", category="", url="/login"))

# Publicly visible pages.
admin.add_view(HelpView(name="Help", url="help"))
admin.add_view(MeshView(session=db, model=Mesh, name="Mesh Raider", url="mesh"))


