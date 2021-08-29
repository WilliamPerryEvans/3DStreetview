import json
from flask import Blueprint, jsonify, request, flash, url_for, redirect
from models.mesh import Mesh
from models.odk import Odk
from odk2odm import odk_requests
from odk2odm import odm_requests
# API components that retrieve or download data from database for use on front end
mesh_api = Blueprint("mesh_api", __name__)

@mesh_api.route("/api/mesh/", methods=["GET"])
def get_meshes():
    """
    API endpoint for getting list of devices and states of devices

    :return:
    """
    meshes = Mesh.query.all()
    return jsonify([d.to_dict() for d in meshes])


@mesh_api.route("/api/mesh/<id>", methods=["POST"])
def post_attachment(id):
    # retrieve content
    content = request.get_json()
    mesh = Mesh.query.get(id)
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

#