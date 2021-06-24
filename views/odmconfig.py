from views.general import UserModelView
from models.odmconfig import Odmconfig
from wtforms import ValidationError

class OdmconfigView(UserModelView):
    can_edit = False
    column_list = (
        Odmconfig.id,
        Odmconfig.name,
        Odmconfig.host,
        Odmconfig.port,
        Odmconfig.user,
        Odmconfig.password,
    )

    column_labels = {
    }
    column_descriptions = {
    }
    form_columns = (
        Odmconfig.name,
        Odmconfig.host,
        Odmconfig.port,
        Odmconfig.user,
        Odmconfig.password,
    )
    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "odmconfig/list.html"
    create_template = "odmconfig/create.html"
    edit_template = "odmconfig/edit.html"
    details_template = "odmconfig/details.html"
