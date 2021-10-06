import os
from flask import flash, redirect, url_for
from flask_security import current_user
from flask_admin.helpers import is_form_submitted
from streetview.views.general import PublicModelView
from streetview.models.game import Game
from flask_admin import form
from zipfile import ZipFile


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

    # ensure that the provided credentials give a suitable response, by querying the most top level API call of ODK Central
    def validate_form(self, form):
        """
        Additional server side validation for ODK server config

        :param form: form
        :return: response
        """
        file_wildcards = [
            ".data",
            "framework.js",
            "loader.js",
            ".wasm"
        ] # files with these wildcards are expected in the zip file, if these are not available, then don't submit
        # assume the form can be submitted (update this with checks)
        prevent_submit = False
        if is_form_submitted():
            # check if a create or edit form was submitted (not a delete), this is when the name attribute is found
            if "zipfile" in form:
                # # first store file
                # fn = form.zipfile._save_file(form.zipfile.data, form.zipfile.data.filename)
                # open zipfile and check if it contains the required files according to wildcards
                try:
                    with ZipFile(form.zipfile.data, 'r') as z:
                        fns = z.namelist()
                        # find mesh, framework, loader and wasm files, if there are multiple, only the first is considered
                        for wildcard in file_wildcards:
                            if len([fn for fn in fns if wildcard in fn]) == 0:
                                prevent_submit = True
                                flash(f"Zipfile {form.zipfile.data.filename} does not contain a file with suffix {wildcard}", "error")
                                break
                except:
                    prevent_submit = True
                    flash(f"File {form.zipfile.data.filename} does not seem to be a zipfile", "error")
                # rewind zipfile stream so that it can be saved in the super form validation
                form.zipfile.data.stream.seek(0)
        # submit the form
        if prevent_submit:
            # remove file
            return False
        return super(GameView, self).validate_form(form)
