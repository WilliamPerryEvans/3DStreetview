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
    # retrieve photo
    print(content)
    res = odk_requests.attachment(odk.url, (odk.user, odk.password), **content["odk_kwargs"])
    # post it on the task
    # retrieve file contents (should only contain "images" but checking for all keys to make sure)
    fields = {"images": (content["odk_kwargs"]["filename"], res.content, "images/jpg")}
    # fields = {}
    # for k in request.files.keys():
    #     file = request.files.get(k)
    #     fields[k] = (file.filename, file.stream.read(), file.content_type)
    try:
        res = odm_requests.post_upload(odm.url, odm.token, odmproject.remote_id, fields=fields, **content["odm_kwargs"])  # odm_kwargs should contain the task_id
        return jsonify(res.json())
    except:
        return f"Page {odm.url} does not exist", 404

#