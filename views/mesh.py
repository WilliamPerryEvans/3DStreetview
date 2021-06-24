from views.general import UserModelView
from models.mesh import Mesh
from flask_admin import form
from wtforms import ValidationError

class MeshView(UserModelView):
    can_edit = False
    column_list = (
        Mesh.id,
        "project",
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
        "project",
        Mesh.latitude,
        Mesh.longitude,
        Mesh.name,
        "zipfile",
        "odmproject",
    )
    form_extra_fields = {"zipfile": form.FileUploadField("Mesh zipfile", base_path="mesh", allowed_extensions=["zip"])}
    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "mesh/list.html"
    create_template = "mesh/create.html"
    #edit_template = "project/edit.html"
    details_template = "mesh/details.html"
