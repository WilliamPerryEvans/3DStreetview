from flask_security import current_user
from views.general import PublicModelView
from models.game import Game
from flask_admin import form

class GameView(PublicModelView):
    @property
    def can_create(self):
        """
        Setting to ensure a Game can only be created by users that are active and authenticated
        :return:
        """
        return current_user.is_active and current_user.is_authenticated

    can_edit = False
    column_list = (
        Game.id,
        Game.name,
        Game.zipfile,
        "mesh",
    )
    column_labels = {
        "name": "Game name",
        "zipfile": "Zip file",
    }
    column_descriptions = {
        "name": "Descriptive name of the game",
        "zipfile": "zipfile containing a Unity compatible .data file",
        "mesh": "Mesh that game belongs to",
    }
    form_extra_fields = {
        "zipfile": form.FileUploadField("Mesh zipfile", base_path="mesh", allowed_extensions=["zip"]),
    }

    form_columns = (
        Game.name,
        "mesh",
        "zipfile",
    )


    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "game/list.html"
    create_template = "game/create.html"
    details_template = "game/details.html"
