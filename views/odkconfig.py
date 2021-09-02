from flask_security import current_user
from wtforms import ValidationError, PasswordField
from views.general import UserModelView
from models.odk import Odk

class OdkconfigView(UserModelView):
    can_edit = False
    column_list = (
        Odk.id,
        Odk.name,
        Odk.host,
        Odk.port,
        Odk.user,
    )
    column_details_list = (
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
        "password_encrypt",
    )

    form_extra_fields = {
        "password_encrypt": PasswordField("Password"),
    }
    # # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "odkconfig/list.html"
    create_template = "odkconfig/create.html"
    edit_template = "odkconfig/edit.html"
    details_template = "odkconfig/details.html"

    def get_query(self):
        """
        Only show Odk configs from this user.

        :return:
        """
        return super(OdkconfigView, self).get_query().filter(Odk.user_id == current_user.id)

    def get_one(self, id):
        """
        Don't allow to access a specific Odk config if it's not from this user.

        :param id:
        :return:
        """
        return super(OdkconfigView, self).get_query().filter_by(id=id).filter(Odk.user_id == current_user.id).one()

    def on_model_change(self, form, model, is_created):
        """
        Link newly created Odk config to the current logged in user on creation.

        :param form:
        :param model:
        :param is_created:
        """
        if is_created:
            model.user_id = current_user.id
