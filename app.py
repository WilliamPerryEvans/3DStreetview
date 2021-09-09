import os
from flask import Flask, redirect, jsonify, url_for
from flask_admin import helpers as admin_helpers
from flask_security import Security, SQLAlchemySessionUserDatastore
from celery import Celery

from models import db
from models.user import User, Role
from views import admin

# Create flask app
user_datastore = SQLAlchemySessionUserDatastore(db, User, Role)
celery = Celery(__name__, broker=os.getenv("CELERY_URL"))

def create_app(config_name):
    app = Flask(config_name, template_folder="templates")
    app.debug = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")
    app.config["FERNET_KEY"] = os.getenv("FERNET_KEY")
    app.config["CELERY_BROKER_URL"] = os.getenv("CELERY_URL")
    # app.config["CELERY_RESULT_BACKEND"] = os.getenv("CELERY_URL")
    app.config["result_backend"] = os.getenv("CELERY_URL")
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


app = create_app(__name__)
# Setup Flask-Security
security = Security(app, user_datastore)


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
