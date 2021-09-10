from flask import has_app_context
from flask_security import current_user
from wtforms import ValidationError, PasswordField
from views.general import UserModelView
from models.odm import Odm

class OdmconfigView(UserModelView):
    @property
    def can_edit(self):
        if has_app_context() and current_user.has_role('admin'):
            return True
        else:
            return False

    @property
    def column_list(self):
        user_column_list = [
            Odm.id,
            Odm.name,
            Odm.host,
            Odm.port,
            Odm.user,
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
            Odm.name,
            Odm.host,
            Odm.port,
            Odm.user,
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
        if not(current_user.has_role("admin")):
            return super(OdmconfigView, self).get_query().filter(Odm.user_id == current_user.id)
        else:
            return super(OdmconfigView, self).get_query()


    def get_one(self, id):
        """
        Don't allow to access a specific Odm config if it's not from this user.

        :param id:
        :return:
        """
        if not(current_user.has_role("admin")):
            return super(OdmconfigView, self).get_query().filter_by(id=id).filter(Odm.user_id == current_user.id).one()
        else:
            return super(OdmconfigView, self).get_query().filter_by(id=id).one()


    def on_model_change(self, form, model, is_created):
        """
        Link newly created Odm config to the current logged in user on creation.

        :param form:
        :param model:
        :param is_created:
        """
        if is_created:
            model.user_id = current_user.id
