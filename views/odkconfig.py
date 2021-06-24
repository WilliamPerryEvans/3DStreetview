from views.general import UserModelView
from models.odkconfig import Odkconfig
from wtforms import ValidationError

class OdkconfigView(UserModelView):
    can_edit = False
    column_list = (
        Odkconfig.id,
        Odkconfig.name,
        Odkconfig.host,
        Odkconfig.port,
        Odkconfig.user,
        Odkconfig.password,
    )

    column_labels = {
    }
    column_descriptions = {
    }
    form_columns = (
        Odkconfig.name,
        Odkconfig.host,
        Odkconfig.port,
        Odkconfig.user,
        Odkconfig.password,
    )
    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "odkconfig/list.html"
    create_template = "odkconfig/create.html"
    edit_template = "odkconfig/edit.html"
    details_template = "odkconfig/details.html"
