from flask import has_app_context, flash
from flask_security import current_user
from flask_admin.helpers import is_form_submitted
from wtforms import ValidationError, PasswordField
from views.general import UserModelView
from models.odk import Odk
from models.odkproject import Odkproject
from models.mesh import Mesh
from odk2odm import odk_requests
from sqlalchemy.exc import IntegrityError

class OdkconfigView(UserModelView):
    @property
    def can_edit(self):
        """
        Only admin users can modify an existing server config, e.g. to give credentials to other users
        :return: boolean
        """
        if has_app_context() and current_user.has_role('admin'):
            return True
        else:
            return False

    @property
    def column_list(self):
        """
        Modify the displayed details in case a user is logged in as admin
        :return: user column list
        """
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
        """
        Modify the displayed details in case a user is logged in as admin
        :return: user form columns
        """
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

    # ensure that the provided credentials give a suitable response, by querying the most top level API call of ODK Central
    def validate_form(self, form):
        """
        Additional server side validation for ODK server config

        :param form: form
        :return: response
        """
        if is_form_submitted():
            # check if a create or edit form was submitted (not a delete), this is when the name attribute is found
            if "name" in form:
                # assume the form can be submitted
                prevent_submit = False
                url = form.host.data.strip('/')
                form.host.data = url  # remove trailing slash from url
                try:
                    res = odk_requests.projects(f"{url}:{form.port.data}", (form.user.data, form.password_encrypt.data))
                except:
                    flash(f"I was not able to find a server on address {url}:{form.port.data}. Is the url and port valid? If so, please check if the server is online.", "error")
                    prevent_submit = True
                if res.status_code == 401:
                    flash(f"Username and password for ODK server at {url}:{form.port.data} are invalid.", "error")
                    prevent_submit = True
                if prevent_submit:
                    # don't submit the form
                    return False
        # submit the form
        return super(OdkconfigView, self).validate_form(form)


    def get_query(self):
        """
        Only show Odk configs from this user.

        :return: queried data
        """
        if not(current_user.has_role("admin")):
            return super(OdkconfigView, self).get_query().filter(Odk.user_id == current_user.id)
        else:
            return super(OdkconfigView, self).get_query()


    def get_one(self, id):
        """
        Don't allow to access a specific Odk config if it's not from this user.

        :param id: id of model
        :return: first in query
        """
        if not(current_user.has_role("admin")):
            return super(OdkconfigView, self).get_query().filter_by(id=id).filter(Odk.user_id == current_user.id).one()
        else:
            return super(OdkconfigView, self).get_query().filter_by(id=id).one()


    def on_model_change(self, form, model, is_created):
        """
        Link newly created Odk config to the current logged in user on creation.

        :param form: form object
        :param model: database model
        :param is_created: True when a new model is created from form
        """
        if is_created:
            model.user_id = current_user.id

    def handle_view_exception(self, e):
        """
        Human readable error message for database integrity errors.

        :param e:
        :return:
        """
        if isinstance(e, IntegrityError):
            flash("ODK config cannot be deleted since it is being used by one or more meshes. You will need to delete those meshes first.", "error")
            return True

        return super(OdkconfigView, self).handle_view_exception(e)
