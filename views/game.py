import json
from views.general import UserModelView
from models.game import Game
from flask import request, redirect, flash
from flask_admin import form, expose
from flask_admin.babel import gettext
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from wtforms.fields import HiddenField

class GameView(UserModelView):
    can_edit = False

    column_list = (
        Game.id,
        Game.name,
        Game.link,
        Game.lng,
        Game.lat,
        Game.zipfile,
        "mesh",
    )
    column_labels = {
        "name": "Game name",
        "link": "Link to the game",
        "zipfile": "Zip file",
    }
    form_extra_fields = {
        "zipfile": form.FileUploadField("Mesh zipfile", base_path="mesh", allowed_extensions=["zip"]),
        "link": form.FileUploadField("link", base_path="mesh", allowed_extensions=["zip"]),
    }

    form_columns = (
        Game.name,
        Game.link,
        Game.lng,
        Game.lat,
        "mesh",
        "zipfile",
    )


    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "game/list.html"
    create_template = "game/create.html"
    details_template = "game/details.html"
