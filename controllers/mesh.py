import json
from flask import Blueprint, jsonify, request, flash, url_for, redirect
from models.mesh import Mesh
# API components that retrieve or download data from database for use on front end
mesh_api = Blueprint("mesh_api", __name__)

@mesh_api.route("/api/get_mesh", methods=["GET"])
def get_mesh():
    """
    API endpoint for getting list of devices and states of devices

    :return:
    """
    meshes = Mesh.query.all()
    return jsonify([d.to_dict() for d in meshes])
