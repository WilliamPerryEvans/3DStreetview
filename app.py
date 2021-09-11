import os
from flask import Flask, redirect, jsonify, url_for, request, flash
from flask_admin import helpers as admin_helpers
from flask_security import Security, SQLAlchemySessionUserDatastore, RegisterForm
from flask_security.signals import user_registered
from flask_mail import Mail, Message
from wtforms import HiddenField, BooleanField
from celery import Celery

from models import db
from models.user import User, Role
from views import admin

# Create flask app
user_datastore = SQLAlchemySessionUserDatastore(db, User, Role)
celery_url = f"redis://:{os.getenv('REDIS_PASSWORD')}@localhost:6379/0"
celery = Celery(__name__, broker=celery_url)

def create_app(config_name):
    app = Flask(config_name, template_folder="templates")
    app.debug = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = (os.getenv("SEND_REGISTER_EMAIL").lower() == "true")
    app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")
    app.config["FERNET_KEY"] = os.getenv("FERNET_KEY")
    # celery_url = f"redis://:{os.getenv('REDIS_PASSWORD')}@localhost:6379/0"
    app.config["CELERY_BROKER_URL"] = celery_url
    app.config["result_backend"] = celery_url
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
    app.config["MAIL_USE_TLS"] = (os.getenv("MAIL_USE_TLS").lower() == "true")
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_SENDER")
    app.config["SECURITY_EMAIL_SENDER"] = os.getenv("MAIL_SENDER")
    # Create admin interface
    admin.init_app(app)
    # after the blueprints are added, also configure celery
    celery.conf.update(app.config)
    from controllers import odk_api
    from controllers import odm_api
    from controllers import odmproject_api
    from controllers import odkproject_api
    from controllers import mesh_api
    app.register_blueprint(mesh_api)
    app.register_blueprint(odk_api)
    app.register_blueprint(odm_api)
    app.register_blueprint(odmproject_api)
    app.register_blueprint(odkproject_api)
    return app

class ExtendedRegisterForm(RegisterForm):
    """
    Make sure that new registrations of users are by default inactive
    """
    active = BooleanField("active")

app = create_app(__name__)
# Setup Flask-Security
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)
mail = Mail(app)

# security = Security(app, user_datastore)


@user_registered.connect_via(app)
def user_registered_sighandler(sender, **kwargs):
    if app.config["SECURITY_SEND_REGISTER_EMAIL"]:
        msg = Message(
            f"New user registration on {request.base_url}",
            # sender=app.config["MAIL_DEFAULT_SENDER"],
            recipients=[app.config["MAIL_USERNAME"]]
        )
        msg.body = f"Please note that a new user from email address {kwargs['user'].email} was registered on {request.url_root}\nPlease activate this user by browsing to {url_for('user.edit_view', id=kwargs['user'].id, _external=True)}"
        mail.send(msg)
        flash(f"Thank you {kwargs['user'].email}. We will evaluate your request and get back to you with instructions", "message")


@app.route("/")
def index():
    return redirect("/dashboard", code=302)

# Provide necessary vars to flask-admin views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,
    )

@app.before_first_request
def create_admin_user():
    """
    In case no roles exist, these are created
    In case no admin user exists, the user is redirected to the page for admin user creation
    Adapted from example https://gist.github.com/skyuplam/ffb1b5f12d7ad787f6e4
    :return:
    """
    user_datastore.find_or_create_role(name="admin", description="Administrator")
    user_datastore.find_or_create_role(name="end-user", description="End user")
    db.commit()

# Resolve database session issues for the combination of Postgres/Sqlalchemy scoped session/Flask-admin.
@app.teardown_appcontext
def shutdown_session(exception=None):
    # load all expired attributes for the given instance
    db.expire_all()

@app.teardown_request
def session_clear(exception=None):
    """
    Resolve database session issues for the combination of Postgres/Sqlalchemy to rollback database transactions after an exception is thrown.
    """
    db.remove()
    if exception and db.is_active:
        db.rollback()


if __name__ == "__main__":

    # Start app
    app.run(host="0.0.0.0", port=5000)
