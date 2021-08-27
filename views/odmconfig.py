from flask_security import current_user
from wtforms import ValidationError, PasswordField
from views.general import UserModelView
from models.odm import Odm

class OdmconfigView(UserModelView):
    can_edit = False
    column_list = (
        Odm.id,
        Odm.name,
        Odm.host,
        Odm.port,
        Odm.user,
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
        "password_encrypt",
    )
    form_extra_fields = {
        "password_encrypt": PasswordField("Password")
    }
    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "odmconfig/list.html"
    create_template = "odmconfig/create.html"
    edit_template = "odmconfig/edit.html"
    details_template = "odmconfig/details.html"

    def get_query(self):
        """
        Only show Odm configs from this user.

        :return:
        """
        return super(OdmconfigView, self).get_query().filter(Odm.user_id == current_user.id)

    def get_one(self, id):
        """
        Don't allow to access a specific Odm config if it's not from this user.

        :param id:
        :return:
        """
        return super(OdmconfigView, self).get_query().filter_by(id=id).filter(Odm.user_id == current_user.id).one()

    def on_model_change(self, form, model, is_created):
        """
        Link newly created Odm config to the current logged in user on creation.

        :param form:
        :param model:
        :param is_created:
        """
        if is_created:
            model.user_id = current_user.id
