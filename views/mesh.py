import json
from views.general import UserModelView
from models.mesh import Mesh
from models.odm import Odm
from models.odk import Odk
from flask import request, redirect, flash
from flask_admin import form, expose
from flask_admin.babel import gettext
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from wtforms.fields import HiddenField

class MeshView(UserModelView):
    def render(self, template, **kwargs):
        # add a database query to available data in Jinja template in the edit page
        # example modified from https://stackoverflow.com/questions/65892714/pass-other-object-data-into-flask-admin-model-view-edit-template
        if template in ['mesh/details.html', 'mesh/create.html']:
            # add odm config and odk config to variables available in jinja template
            odmconfigs = Odm.query.all()
            odkconfigs = Odk.query.all()
            kwargs["odm_configs"] = odmconfigs
            kwargs["odk_configs"] = odkconfigs

        return super(MeshView, self).render(template, **kwargs)

    details_modal = True
    can_edit = True
    column_list = (
        Mesh.id,
        Mesh.latitude,
        Mesh.longitude,
        Mesh.name,
        Mesh.zipfile,
        Mesh.status,
        "odmproject_id",
        "odkproject_id",
    )
    column_labels = {
        "name": "Mesh name",
        "zipfile": "Zip file",
    }
    # column_descriptions = {
    # }
    form_extra_fields = {
        "odmproject_id": HiddenField("odmproject_id"),
        "odkproject_id": HiddenField("odkproject_id"),
        "zipfile": form.FileUploadField("Mesh zipfile", base_path="mesh", allowed_extensions=["zip"]),
    }

    form_columns = (
        Mesh.latitude,
        Mesh.longitude,
        Mesh.name,
        "zipfile",
        "odmproject_id",
        "odkproject_id",
    )
    column_extra_row_actions = [  # Add a new action button
        EndpointLinkRowAction("fa fa-exchange", ".odk2odm"),
    ]


    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "mesh/list.html"
    create_template = "mesh/create.html"
    details_modal_template = "mesh/details.html"
    odk2odm_template = "mesh/odk2odm.html"

    @expose("/odk2odm", methods=("GET",))
    def odk2odm(self):
        """The method you need to call"""
        """
            Details model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        # odk2odm behaves the same as details
        if not self.can_view_details:
            return redirect(return_url)

        # retrieve model
        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('Record does not exist.'), 'error')
            return redirect(return_url)

        template = self.odk2odm_template

        return self.render(
            template,
            model=model,
            details_columns=self._details_columns,
            get_value=self.get_detail_value,
            return_url=return_url
        )
