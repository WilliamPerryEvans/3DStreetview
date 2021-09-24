from flask import Blueprint, jsonify, request
from flask_security import login_required, current_user
from models.odmproject import Odmproject
from models import db
# API components that retrieve or download data from database for use on front end
odmproject_api = Blueprint("odmproject_api", __name__)
from jsonschema import validate, ValidationError


schema = {
    "type": "object",
    "properties": {
        "odm_id": {"type": "number"},
        "remote_id": {"type": "number"},
    },
    "minProperties": 2,
    "additionalProperties": False
}

@odmproject_api.before_request
def before_request():
    """
    Any request in this controller can only be performed by logged in users
    :return: http response
    """
    if current_user.is_anonymous:
        return jsonify("Forbidden"), 401

@odmproject_api.route("/api/odmproject/create_project", methods=["POST"])
@login_required
def create_project():
    """
    API endpoint for posting a new ODM project that has a one-to-one relationship with a mesh
    required kwargs are provided through the request content in json

    :return: http response
    """
    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    odm_project = Odmproject(**content)
    db.add(odm_project)
    db.commit()
    db.refresh(odm_project)
    return jsonify(odm_project.to_dict())

@odmproject_api.errorhandler(ValidationError)
@odmproject_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for ODM project API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for ODM project", "message": str(e)}), 400

