from flask import Blueprint, jsonify, request
from models.odkproject import Odkproject
from models import db
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

@odkproject_api.route("/api/odkproject/create_project", methods=["POST"])
def create_project():
    """
    API endpoint for posting a new ODK project that has a one-to-one relationship with a mesh

    :return:
    """
    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    odm_project = Odkproject(**content)
    db.add(odm_project)
    db.commit()
    db.refresh(odm_project)
    return jsonify(odm_project.to_dict())

@odkproject_api.errorhandler(ValidationError)
@odkproject_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for ODK project API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for ODK project", "message": str(e)}), 400
