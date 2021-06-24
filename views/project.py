from views.general import UserModelView
from models.project import Project
from wtforms import ValidationError

class ProjectView(UserModelView):
    can_edit = False
    column_list = (
        Project.id,
        Project.name,
        Project.description,
    )

    column_labels = {
    }
    column_descriptions = {
    }
    form_columns = (
        Project.name,
        Project.description,
    )
    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "project/list.html"
    create_template = "project/create.html"
    edit_template = "project/edit.html"
    details_template = "project/details.html"
