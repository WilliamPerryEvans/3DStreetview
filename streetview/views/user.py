from flask_security import utils
from wtforms.fields import PasswordField
from streetview.views.general import AdminModelView
# Customized User model for SQL-Admin
class UserView(AdminModelView):
    """
    Admin page for users, modified from https://github.com/sasaporta/flask-security-admin-example/blob/master/main.py
    """
    # Don't display the password on the list of Users
    column_exclude_list = list = ('username', 'password', 'last_login_at', 'current_login_at', 'last_login_ip', 'current_login_ip', 'login_count', 'confirmed_at')
    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('username', 'password', 'last_login_at', 'current_login_at', 'last_login_ip', 'current_login_ip', 'login_count', 'confirmed_at')

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserView, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):
        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.hash_password(model.password2)
