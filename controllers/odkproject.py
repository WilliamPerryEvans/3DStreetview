import json
from flask import Blueprint, jsonify, request, flash, url_for, redirect
from models.odkproject import Odkproject
# API components that retrieve or download data from database for use on front end
odkproject_api = Blueprint("odkproject_api", __name__)

@odkproject_api.route("/api/odkproject/create_project", methods=["POST"])
def create_project():
    """
    API endpoint for getting list of devices and states of devices

    :return:
    """

    # FIXME: make func
    pass
