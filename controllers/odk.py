import json
from flask import Blueprint, jsonify, request, flash, url_for, redirect
# from models.mesh import Mesh
# API components that retrieve or download data from database for use on front end
odk_api = Blueprint("odk_api", __name__)

@odk_api.route("/api/odk/create_project", methods=["GET"])
def create_project():
    """
    API endpoint for getting list of devices and states of devices

    :return:
    """
    # FIXME: make func
    pass
