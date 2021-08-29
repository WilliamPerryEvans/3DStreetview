from views.general import UserModelView
from models.odk import Odk
from wtforms import ValidationError, PasswordField

class OdkconfigView(UserModelView):
    can_edit = False
    column_list = (
        Odk.id,
        Odk.name,
        Odk.host,
        Odk.port,
        Odk.user,
    )

    column_labels = {
    }
    column_descriptions = {
    }
    form_columns = (
        Odk.name,
        Odk.host,
        Odk.port,
        Odk.user,
        "password",
    )

    form_extra_fields = {
        "password": PasswordField("password"),
    }
    # # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "odkconfig/list.html"
    create_template = "odkconfig/create.html"
    edit_template = "odkconfig/edit.html"
    details_template = "odkconfig/details.html"
