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
    details_modal = True
    can_edit = False

    column_list = (
        Game.id,
        Game.name,
        Game.zipfile,
        "mesh_id",
    )
    column_labels = {
        "name": "Mesh name",
        "zipfile": "Zip file",
    }
    form_extra_fields = {
        "zipfile": form.FileUploadField("Mesh zipfile", base_path="mesh", allowed_extensions=["zip"]),
    }

    form_columns = (
        Game.name,
        "mesh_id",
        "zipfile",
    )


    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "game/list.html"
    create_template = "game/create.html"
    details_modal_template = "game/details.html"
