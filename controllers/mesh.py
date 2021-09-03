import time
from flask import Blueprint, jsonify, request, url_for
from flask_security import login_required, current_user
from models.mesh import Mesh
from odk2odm import odk_requests
from odk2odm import odm_requests
# API components that retrieve or download data from database for use on front end

mesh_api = Blueprint("mesh_api", __name__)

from app import celery

@celery.task(bind=True)
def test_job(self):
    print("Running job as a Thread!")
    for i in range(10):
        print(f"Processing {i}/10")
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i,
                'total': 10,
                'status': "Working..."
            }
        )
        time.sleep(10)
    return {
        'current': 100,
        'total': 100,
        'status': 'Job completed!',
        'result': 42
    }

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


@mesh_api.route("/api/mesh/odk2odm/<id>", methods=["POST"])
@login_required
def submit_upload():
    # retrieve content
    content = request.get_json()
    try:
        mesh = Mesh.query.filter_by(id=id).filter(Mesh.user_id == current_user.id).one()
    except:
        return jsonify("Access denied"), 403
    # retrieve the relevant odk and odm server and project details
    odk = mesh.odkproject.odk
    odmproject = mesh.odmproject
    odm = odmproject.odm  # odm server record
    odm_server = {
        "url": odm.url, "token": odm.token
    }
    odk_server = {
        "url": odk.url,
        "auth": (odk.user, odk.password)
    }

    upload_task = odk2odm(odk.to_dict(), odm.to_dict(), )
    odk

    task = test_job.apply_async()
    print(task.id)
    return jsonify({}), 202, {'Location': url_for('mesh_api.taskstatus',
                                                  task_id=task.id)}

@mesh_api.route("/api/mesh/test", methods=["GET"])
@login_required
def mesh_test():
    task = test_job.apply_async()
    print(task.id)
    return jsonify({}), 202, {'Location': url_for('mesh_api.taskstatus',
                                                  task_id=task.id)}

# status api request
@mesh_api.route('/status/<task_id>')
def taskstatus(task_id):
    task = test_job.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)