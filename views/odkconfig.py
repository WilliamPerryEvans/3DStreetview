from flask import has_app_context
from flask_security import current_user
from wtforms import ValidationError, PasswordField
from views.general import UserModelView
from models.odk import Odk

class OdkconfigView(UserModelView):
    @property
    def can_edit(self):
        if has_app_context() and current_user.has_role('admin'):
            return True
        else:
            return False

    @property
    def column_list(self):
        user_column_list = [
            Odk.id,
            Odk.name,
            Odk.host,
            Odk.port,
            Odk.user,
        ]
        if has_app_context() and current_user.has_role('admin'):
            user_column_list.append("app_user")
        return user_column_list

    @property
    def _list_columns(self):
        return self.get_list_columns()

    @_list_columns.setter
    def _list_columns(self, value):
        pass

    @property
    def form_columns(self):
        user_form_columns = [
            Odk.name,
            Odk.host,
            Odk.port,
            Odk.user,
            "password_encrypt",
        ]
        if has_app_context() and current_user.has_role('admin'):
            user_form_columns.append("app_user")
        return user_form_columns

    @property
    def _create_form_class(self):
        return self.get_create_form()

    @_create_form_class.setter
    def _create_form_class(self, value):
        pass

    @property
    def _edit_form_class(self):
        return self.get_edit_form()

    @_edit_form_class.setter
    def _edit_form_class(self, value):
        pass

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
        if not(current_user.has_role("admin")):
            return super(OdkconfigView, self).get_query().filter(Odk.user_id == current_user.id)
        else:
            return super(OdkconfigView, self).get_query()


    def get_one(self, id):
        """
        Don't allow to access a specific Odk config if it's not from this user.

        :param id:
        :return:
        """
        if not(current_user.has_role("admin")):
            return super(OdkconfigView, self).get_query().filter_by(id=id).filter(Odk.user_id == current_user.id).one()
        else:
            return super(OdkconfigView, self).get_query().filter_by(id=id).one()


    def on_model_change(self, form, model, is_created):
        """
        Link newly created Odk config to the current logged in user on creation.

        :param form:
        :param model:
        :param is_created:
        """
        if is_created:
            model.user_id = current_user.id
