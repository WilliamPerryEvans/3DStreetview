import time
from flask import Blueprint, jsonify, request
from flask_security import login_required, current_user
from models.mesh import Mesh
from odk2odm import odk_requests
from odk2odm import odm_requests
# API components that retrieve or download data from database for use on front end

mesh_api = Blueprint("mesh_api", __name__)

from app import celery

@celery.task(bind=True)
def odk2odm():
    time.sleep(10)



@mesh_api.before_request
def before_request():
    if current_user.is_anonymous:
        return jsonify("Forbidden"), 401

@mesh_api.route("/api/mesh/", methods=["GET"])
@login_required
def get_meshes():
    """
    API endpoint for getting list of meshes available to currently logged in user

    :return:
    """
    meshes = Mesh.query.filter_by(id=id).filter(Mesh.user_id == current_user.id).all()
    return jsonify([d.to_dict() for d in meshes])


@mesh_api.route("/api/mesh/<id>", methods=["POST"])
@login_required
def post_attachment(id):
    # retrieve content
    content = request.get_json()
    try:
        mesh = Mesh.query.filter_by(id=id).filter(Mesh.user_id == current_user.id).one()
    except:
        return jsonify("Access denied"), 403

    # mesh = Mesh.query.get(id)
    odk = mesh.odkproject.odk
    odmproject = mesh.odmproject
    odm = odmproject.odm  # odm server record
    # try if file already exists by checking for a thumbnail
    res = odm_requests.get_thumbnail(base_url=odm.url, token=odm.token, project_id=odmproject.remote_id, filename=content["odk_kwargs"]["filename"], **content["odm_kwargs"])
    if res.status_code == 200:
        return jsonify(f"{content['odk_kwargs']['filename']} is already present in ODM task")
    # retrieve photo
    print(content)
    res = odk_requests.attachment(odk.url, (odk.user, odk.password), **content["odk_kwargs"])
    # post it on the task
    # retrieve file contents (should only contain "images" but checking for all keys to make sure)
    fields = {"images": (content["odk_kwargs"]["filename"], res.content, "images/jpg")}
    try:
        res = odm_requests.post_upload(odm.url, odm.token, odmproject.remote_id, fields=fields, **content["odm_kwargs"])  # odm_kwargs should contain the task_id
        if res.status_code == 200:
            return jsonify(f"{content['odk_kwargs']['filename']} uploaded")
        else:
            return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404
