import json
from flask import Blueprint, jsonify, request
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

@odmproject_api.route("/api/odmproject/create_project", methods=["POST"])
def create_project():
    """
    API endpoint for posting a new ODM project that has a one-to-one relationship with a mesh

    :return:
    """
    content = request.get_json(silent=True)
    validate(instance=content, schema=schema)
    odm_project = Odmproject(**content)
    db.add(odm_project)
    db.commit()
    db.refresh(odm_project)
    return jsonify(odm_project.to_dict())

