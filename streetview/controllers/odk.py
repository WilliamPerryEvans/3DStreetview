import io
from flask import Blueprint, jsonify, request, make_response
from streetview.models.odk import Odk
from odk2odm import odk_requests
from flask_security import login_required, current_user

# API components that retrieve or download data from database for use on front end
odk_api = Blueprint("odk_api", __name__)

def get_odk(id):
    """
    Retrieve config with id from database, check if it belongs to user
    :param id: odm id
    :return: if the chosen project does not belong to the user, then return a 403 response, else return the Odm model
    """
    try:
        return Odk.query.filter_by(id=id).filter(Odk.user_id == current_user.id).one()
    except:
        return jsonify("Access denied"), 403

@odk_api.before_request
def before_request():
    """
    Any request in this controller can only be performed by logged in users
    :return:
    """
    if current_user.is_anonymous:
        return jsonify("Forbidden"), 401

@odk_api.route("/api/odk/<id>/users", methods=["GET"])
@login_required
def get_users(id):
    """
    API endpoint for getting list of users on ODK Central server

    :param id: int - ODK server id
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.users(odk.url, (odk.user, odk.password))
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects", methods=["GET"])
@login_required
def get_projects(id):
    """
    API endpoint for getting list of ODM projects from odm config

    :param id: int - ODK server id
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.projects(odk.url, (odk.user, odk.password))
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>", methods=["GET"])
@login_required
def get_project(id, project_id):
    """
    API endpoint for getting details of project

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.project(odk.url, (odk.user, odk.password), project_id)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>/forms", methods=["GET"])
@login_required
def get_forms(id, project_id):
    """
    API endpoint for getting forms of specific project

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.forms(odk.url, (odk.user, odk.password), project_id)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>/forms/<form_id>", methods=["GET"])
@login_required
def get_form(id, project_id, form_id):
    """
    API endpoint for getting single form of specific project

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :param form_id: str - ODK form id
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.form(odk.url, (odk.user, odk.password), project_id, form_id)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>/streetview-users", methods=["GET"])
@login_required
def get_app_users(id, project_id):
    """
    API endpoint for getting streetview-users of specific project

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.app_users(odk.url, (odk.user, odk.password), project_id)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>/forms/<form_id>/submissions", methods=["GET"])
@login_required
def get_submissions(id, project_id, form_id):
    """
    API endpoint for getting submissions of given form in given project

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :param form_id: str - ODK form id
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.submissions(odk.url, (odk.user, odk.password), project_id, form_id)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>/forms/<form_id>/submissions.csv.zip", methods=["GET"])
@login_required
def get_csv_submissions(id, project_id, form_id):
    """
    API endpoint for getting submissions of given form in given project in csv format

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :param form_id: str - ODK form id
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.csv_submissions(odk.url, (odk.user, odk.password), project_id, form_id)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>/forms/<form_id>/submissions/<instance_id>/attachments", methods=["GET"])
@login_required
def get_attachments(id, project_id, form_id, instance_id):
    """
    API endpoint for getting list of attachments of single submission of given form in given project

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :param form_id: str - ODK form id
    :param instance_id: int - record number
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.attachment_list(odk.url, (odk.user, odk.password), project_id, form_id, instance_id)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>/forms/<form_id>/submissions/<instance_id>/attachments/<filename>", methods=["GET"])
@login_required
def get_attachment(id, project_id, form_id, instance_id, filename):
    """
    API endpoint for getting a single attachment file of single submission of given form in given project

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :param form_id: str - ODK form id
    :param instance_id: int - record number
    :param filename: str - filename attachment belonging to record
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.attachment(odk.url, (odk.user, odk.password), project_id, form_id, instance_id, filename)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/key/<token>/projects/<project_id>", methods=["GET"])
@login_required
def get_qr_code(id, project_id, token):
    """
    API endpoint for getting a  QR code for streetview-user with specified token, for given project

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :param token: str - streetview user's token
    :return: http response
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    general = {
        "form_update_mode": "match_exactly",
        "autosend": "wifi_and_cellular",
    }
    try:
        result = odk_requests.get_qr_code(odk.url, (odk.user, odk.password), project_id, token, admin={}, general=general)
    except:
        return f"Page {odk.url} does not exist", 404
    # convert response into a full response with byte stream
    try:
        img_byte = io.BytesIO()
        # store data in a byte stream
        result[0].save(img_byte, format="PNG")
        # rewind byte stream
        img_byte.seek(0)
        # create response and send
        res = make_response(img_byte.read())
        res.headers["Content-Type"] = "image/png"
        return res
    except:
        return "Not able to convert project into a valid QR-code", 400

# ================ POST ====================

@odk_api.route("/api/odk/<id>/projects/", methods=["POST"])
@login_required
def post_project(id):
    """
    API endpoint for posting a new project on ODK Central server
    Expects a json with recipe {"name": <PROJECT NAME>} as payload
    :param id: int - ODK server id
    :return: http response
    """
    try:
        project_name = request.get_json()["name"]
    except:
        return 'payload did not contain recipe {"name": <PROJECT NAME>}', 400
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.create_project(odk.url, (odk.user, odk.password), project_name=project_name)
        return jsonify(res.json())
    except:
        return f"Retrieval from {odk.url} failed", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>/streetview-users", methods=["POST"])
@login_required
def post_app_user(id, project_id):
    """
    API endpoint for posting a new streetview user on ODK Central server
    Expects a json with recipe {"displayName": <APP USERNAME>} as payload

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :return: http response
    """
    try:
        app_user_name = request.get_json()["displayName"]
    except:
        return 'payload did not contain recipe {"displayName": <APP USERNAME>}', 400
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk

    try:
        res = odk_requests.create_app_user(odk.url, (odk.user, odk.password), project_id, app_user_name=app_user_name)
        return jsonify(res.json())
    except:
        return f"Page {odk.url} does not exist", 404


@odk_api.route("/api/odk/<id>/projects/<project_id>/forms/<form_id>/assignments/<role_id>/<actor_id>", methods=["POST"])
@login_required
def update_role_app_user(id, project_id, form_id, role_id, actor_id):
    """
    API endpoint for updating role of existing streetview user in project on ODK Central server

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :param form_id: str - ODK form id
    :param role_id: int - role of ODK streetview user (2 is to give access)
    :param actor_id: int - id of streetview user
    :return: http response
    """

    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.update_role_app_user(odk.url, (odk.user, odk.password), project_id, form_id, actor_id, role_id)
        return jsonify(res.json())
    except:
        return f"Page {odk.url} does not exist", 404

@odk_api.route("/api/odk/<id>/projects/<project_id>/forms", methods=["POST"])
@login_required
def post_form(id, project_id):
    """
    API endpoint for posting a new form on ODK Central server
    this is a multipart form request, in which one file has to be submitted of the content-type
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    :return: http response
    """
    files = request.files
    if len(files) != 1:
        return f"Request contained {len(files)} files, where 1 file is expected", 400
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    for k in files.keys():
        content = files.get(k)
    if content.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return f'File {content.filename} should be of type "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" but has type "{content.content_type}', 400
    try:
        res = odk_requests.create_form(odk.url, (odk.user, odk.password), project_id, name=k, data=content.stream.read())
        return jsonify(res.json())
    except:
        return f"Page {odk.url} does not exist", 404


# ================ DELETE ====================

@odk_api.route("/api/odk/<id>/projects/<project_id>", methods=["DELETE"])
@login_required
def delete_project(id, project_id):
    """
    API endpoint for deleting a project from ODK Central server

    :param id: int - ODK server id
    :param project_id: int - ODK remote project id
    """
    odk = get_odk(id)
    if not(isinstance(odk, Odk)):
        return odk
    try:
        res = odk_requests.delete_project(odk.url, (odk.user, odk.password), project_id)
        return jsonify(res.json())
    except:
        return f"Page {odk.url} does not exist", 404

