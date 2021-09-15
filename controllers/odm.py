from flask import Blueprint, jsonify, request, Response, make_response
from flask_security import current_user, login_required
from models.odm import Odm
from odk2odm import odm_requests
# API components that retrieve or download data from database for use on front end
odm_api = Blueprint("odm_api", __name__)

def get_odm(id):
    """
    Retrieve config with id from database, check if it belongs to user
    :param id: odm id
    :return: if the chosen project does not belong to the user, then return a 403 response, else return the Odm model
    """
    try:
        return Odm.query.filter_by(id=id).filter(Odm.user_id == current_user.id).one()
    except:
        return jsonify("Access denied"), 403

@odm_api.before_request
def before_request():
    if current_user.is_anonymous:
        return jsonify("Forbidden"), 401

@odm_api.route("/api/odm/<id>/token-auth", methods=["GET"])
@login_required
def get_token(id):
    """
    Get a token for access to ODM server
    :param id: odm configuration id
    :return:
    """
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.token_auth(odm.url, odm.user, odm.password)
        return res.json()['token'], res.status_code
    except:
        return f"Retrieval from {odm.url} failed", 404


@odm_api.route("/api/odm/<id>/projects", methods=["GET"])
@login_required
def get_projects(id):
    """
    API endpoint for getting list of ODM projects from odm config
    :param id: odm configuration id
    :return:
    """
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.get_projects(odm.url, odm.token)
        if res.status_code == 403:
            return f"Authentication failed", 403
        return jsonify(res.json())
    except:
        return f"Retrieval from {odm.url} failed", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>", methods=["GET"])
@login_required
def get_project(id, project_id):
    """
    API endpoint for getting details of project

    :return:
    """
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.get_project(odm.url, odm.token, project_id)
        if res.status_code == 403:
            return f"Authentication failed", 403
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>", methods=["GET"])
@login_required
def get_task(id, project_id, task_id):
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.get_task(odm.url, odm.token, project_id, task_id)
        # current_app.logger.info(res.json())
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/images/download/<filename>", methods=["GET"])
@login_required
def get_image(id, project_id, task_id, filename):
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.get_image(odm.url, odm.token, project_id, task_id, filename)
        return res
    except:
        return f"Page {odm.url} does not exist", 404

@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/download/<asset>", methods=["GET"])
@login_required
def get_asset(id, project_id, task_id, asset):
    odm = get_odm(id)
    if not (isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.get_asset(odm.url, odm.token, project_id, task_id, asset)

        return (res.content, res.status_code, res.headers.items())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/images/thumbnail/<filename>", methods=["GET"])
@login_required
def get_thumbnail(id, project_id, task_id, filename):
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.get_image(odm.url, odm.token, project_id, task_id, filename)
        return res
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/", methods=["POST"])
@login_required
def post_project(id):
    """
    API endpoint for posting a new project

    :return:
    """
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.post_project(odm.url, odm.token, data=request.get_json())
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/", methods=["POST"])
@login_required
def post_task(id, project_id):
    # TODO: allow for passing of options from allowed list
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    # request token
    try:
        res = odm_requests.post_task(odm.url, odm.token, project_id, data=request.get_json())
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/upload/", methods=["POST"])
@login_required
def post_upload(id, project_id, task_id):
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    # retrieve file contents (should only contain "images" but checking for all keys to make sure)
    fields = {}
    for k in request.files.keys():
        file = request.files.get(k)
        fields[k] = (file.filename, file.stream.read(), file.content_type)
    try:
        res = odm_requests.post_upload(odm.url, odm.token, project_id, task_id, fields=fields)
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/cancel/", methods=["POST"])
@login_required
def post_cancel(id, project_id, task_id):
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    # retrieve file contents (should only contain "images" but checking for all keys to make sure)
    try:
        res = odm_requests.post_cancel(odm.url, odm.token, project_id, task_id)
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404

@odm_api.route("/api/odm/<id>/projects/<project_id>", methods=["DELETE"])
@login_required
def delete_project(id, project_id):
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.delete_project(odm.url, odm.token, project_id)
        return jsonify("Success", 200)
    except:
        return f"Page {odm.url} does not exist", 404



@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/remove/", methods=["POST"])
@login_required
def delete_task(id, project_id, task_id):
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.delete_task(odm.url, odm.token, project_id, task_id)
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/commit/", methods=["POST"])
@login_required
def post_commit(id, project_id, task_id):
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.post_commit(odm.url, odm.token, project_id, task_id)
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/restart/", methods=["POST"])
@login_required
def post_restart(id, project_id, task_id):
    odm = get_odm(id)
    if not(isinstance(odm, Odm)):
        return odm
    try:
        res = odm_requests.post_restart(odm.url, odm.token, project_id, task_id)
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404
