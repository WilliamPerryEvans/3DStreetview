from flask import Blueprint, jsonify, request
from flask_security import login_required, current_user
from streetview.models.odkproject import Odkproject
from streetview.models import db
# API components that retrieve or download data from database for use on front end
odkproject_api = Blueprint("odkproject_api", __name__)
from jsonschema import validate, ValidationError

schema = {
    "type": "object",
    "properties": {
        "odk_id": {"type": "number"},
        "remote_id": {"type": "number"},
    },
    "minProperties": 2,
    "additionalProperties": False
}

@odkproject_api.before_request
def before_request():
    """
    Any request in this controller can only be performed by logged in users
    :return: http response
    """
    if current_user.is_anonymous:
        return jsonify("Forbidden"), 401

@odkproject_api.route("/api/odkproject/create_project", methods=["POST"])
@login_required
def create_project():
    """
    API endpoint for posting a new ODK project that has a one-to-one relationship with a mesh
    required kwargs are provided through the request content in json
    :return: http response
    """
    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    odk_project = Odkproject(**content)
    db.add(odk_project)
    db.commit()
    db.refresh(odk_project)
    return jsonify(odk_project.to_dict())

@odkproject_api.errorhandler(ValidationError)
@odkproject_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for ODK project API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for ODK project", "message": str(e)}), 400
