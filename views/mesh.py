from views.general import UserModelView
from models.mesh import Mesh
from models.odm import Odm
from flask_admin import form
from flask_admin.babel import gettext
from flask import redirect, request, flash
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from wtforms import ValidationError

class MeshView(UserModelView):
    def render(self, template, **kwargs):
        # add a database query to available data in Jinja template in the edit page
        # example modified from https://stackoverflow.com/questions/65892714/pass-other-object-data-into-flask-admin-model-view-edit-template
        if template == 'mesh/edit.html':
            # Get the model, this is just the first few lines of edit_view method
            return_url = get_redirect_target() or self.get_url('.index_view')
            if not self.can_edit:
                return redirect(return_url)

            id = get_mdict_item_or_list(request.args, 'id')
            if id is None:
                return redirect(return_url)

            model = self.get_one(id)

            if model is None:
                flash(gettext('Record does not exist.'), 'error')
                return redirect(return_url)
            odmconfigs = Odm.query.all()  # .query.filter_by(email=model.email)
            kwargs['odm_configs'] = odmconfigs
        return super(MeshView, self).render(template, **kwargs)

    can_edit = True
    column_list = (
        "config",
        Mesh.id,
        Mesh.latitude,
        Mesh.longitude,
        Mesh.name,
        Mesh.zipfile,
        "odmproject",
        Mesh.status,
    )
    column_labels = {
        "name": "Mesh name",
        "zipfile": "Zip file"
    }
    column_descriptions = {
    }
    form_columns = (
        Mesh.latitude,
        Mesh.longitude,
        Mesh.name,
        "zipfile",
        "odmproject",
    )
    form_extra_fields = {
        "zipfile": form.FileUploadField("Mesh zipfile", base_path="mesh", allowed_extensions=["zip"]),
    }

    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "mesh/list.html"
    create_template = "mesh/create.html"
    edit_template = "mesh/edit.html"
    details_template = "mesh/details.html"
