import flask_admin as admin
# Models for CRUD views.
from models import db
from views.general import LogoutMenuLink, LoginMenuLink, UserModelView, AdminModelView
from views.help import HelpView
from views.mesh import MeshView
from views.odkconfig import OdkconfigView
from views.odmconfig import OdmconfigView
from views.game import GameView
from views.user import UserView

from models.mesh import Mesh
from models.game import Game
from models.odk import Odk
from models.odm import Odm
from models.user import User
from models.user import Role

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

