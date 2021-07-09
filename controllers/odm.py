from flask import Blueprint, jsonify, request
from models.odm import Odm
from odk2odm import odm_req
# API components that retrieve or download data from database for use on front end
odm_api = Blueprint("odm_api", __name__)


@odm_api.route("/api/odm/<id>/token-auth", methods=["GET"])
def get_token(id):
    """
    Get a token for access to ODM server
    :param id: odm configuration id
    :return:
    """
    odm = Odm.query.get(id)
    try:
        res = odm_req.token_auth(odm.url, odm.user, odm.password)
        return res.json()['token'], res.status_code
    except:
        return f"Retrieval from {odm.url} failed", 404


@odm_api.route("/api/odm/<id>/projects", methods=["GET"])
def get_projects(id):
    """
    API endpoint for getting list of ODM projects from odm config
    :param id: odm configuration id
    :return:
    """
    odm = Odm.query.get(id)
    # request token
    try:
        res = odm_req.get_projects(odm.url, odm.token)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odm.url} failed", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>", methods=["GET"])
def get_project(id, project_id):
    """
    API endpoint for getting details of project

    :return:
    """
    # retrieve config from database
    odm = Odm.query.get(id)
    try:
        res = odm_req.get_project(odm.url, odm.token, project_id)
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/", methods=["POST"])
def post_project(id):
    """
    API endpoint for getting list of devices and states of devices

    :return:
    """
    # retrieve config from database
    odm = Odm.query.get(id)
    try:
        res = odm_req.post_project(odm.url, odm.token, data=request.get_json())
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>", methods=["GET"])
def get_task(id, project_id, task_id):
    # retrieve config from database
    odm = Odm.query.get(id)
    try:
        res = odm_req.get_task(odm.url, odm.token, project_id, task_id)
        # current_app.logger.info(res.json())
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404



@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/", methods=["POST"])
def post_task(id, project_id):
    # TODO: allow for passing of options from allowed list
    # retrieve config from database
    odm = Odm.query.get(id)
    # request token
    try:
        res = odm_req.post_task(odm.url, odm.token, project_id, data=request.get_json())
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/upload/", methods=["POST"])
def post_upload(id, project_id, task_id):
    # retrieve config from database
    odm = Odm.query.get(id)
    # retrieve file contents (should only contain "images" but checking for all keys to make sure)
    fields = {}
    for k in request.files.keys():
        file = request.files.get(k)
        fields[k] = (file.filename, file.stream.read(), file.content_type)
    try:
        res = odm_req.post_upload(odm.url, odm.token, project_id, task_id, fields=fields)
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/commit/", methods=["POST"])
def commit(id, project_id, task_id):
    # retrieve config from database
    odm = Odm.query.get(id)
    try:
        res = odm_req.post_commit(odm.url, odm.token, project_id, task_id)
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404

