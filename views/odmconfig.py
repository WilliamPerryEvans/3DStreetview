from views.general import UserModelView
from models.odm import Odm
from wtforms import ValidationError

class OdmconfigView(UserModelView):
    can_edit = False
    column_list = (
        Odm.id,
        Odm.name,
        Odm.host,
        Odm.port,
        Odm.user,
        Odm.password,
    )

    column_labels = {
    }
    column_descriptions = {
    }
    form_columns = (
        Odm.name,
        Odm.host,
        Odm.port,
        Odm.user,
        Odm.password,
    )
    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "odmconfig/list.html"
    create_template = "odmconfig/create.html"
    edit_template = "odmconfig/edit.html"
    details_template = "odmconfig/details.html"
