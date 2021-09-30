import flask_admin as admin
# Models for CRUD views.
from streetview.models import db
from streetview.views.general import LogoutMenuLink, LoginMenuLink, AdminModelView
from streetview.views.help import HelpView
from streetview.views.mesh import MeshView
from streetview.views.odkconfig import OdkconfigView
from streetview.views.odmconfig import OdmconfigView
from streetview.views.game import GameView
from streetview.views.user import UserView

from streetview.models.mesh import Mesh
from streetview.models.game import Game
from streetview.models.odk import Odk
from streetview.models.odm import Odm
from streetview.models.user import User
from streetview.models.user import Role

import random
from datetime import datetime
random.seed(datetime.now().timestamp())

admin = admin.Admin(name="3D Streetview", template_mode="bootstrap4", url="/dashboard", base_template="base.html")

# Login/logout menu links.
admin.add_link(LogoutMenuLink(name="Logout", category="", url="/logout"))
admin.add_link(LoginMenuLink(name="Login", category="", url="/login", icon_type="image-url", icon_value=f"/static/img/undraw_profile_0.svg"))

# Publicly visible pages.
admin.add_view(OdkconfigView(session=db, model=Odk, name="ODK configuration", url="odkconfig", category="Servers"))
admin.add_view(OdmconfigView(session=db, model=Odm, name="ODM configuration", url="odmconfig", category="Servers"))
admin.add_view(MeshView(session=db, model=Mesh, name="Meshes", url="mesh"))
admin.add_view(GameView(session=db, model=Game, name="Games", url="game", menu_icon_type="fab", menu_icon_value="fa-unity"))
admin.add_view(HelpView(name="Help", url="help", menu_icon_type="fas", menu_icon_value="fa-info"))
# Add Flask-Admin views for Users and Roles
admin.add_view(UserView(User, db))
admin.add_view(AdminModelView(Role, db))

