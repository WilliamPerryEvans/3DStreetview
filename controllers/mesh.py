import time
from flask import Blueprint, jsonify, request, url_for, flash
from flask_security import login_required, current_user
from models.mesh import Mesh
from models import db
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
        time.sleep(1)
    return {
        'current': 100,
        'total': 100,
        'status': 'Job completed!',
        'result': 42
    }


@celery.task(bind=True)
def odk2odm(self, submissions=[], odk={}, odm={}):
    def transfer(att, state="PROGRESS"):
        """
        subroutine to transfer one file
        :param att: attachment details from odk server
        :return:
        """
        res = odm_requests.get_thumbnail(filename=att["name"], **odm)
        if res.status_code == 200:
            msg = f"{att['name']} already uploaded, so skipping..."
            print(msg)
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': n,
                    'total': len(submissions),
                    'status': msg
                }
            )
            return
        # retrieve photo
        res = odk_requests.attachment(instanceId=sub["instanceId"], filename=att["name"], **odk)
        try:
            if res.status_code != 200:
                # something went wrong, so report that
                state = "ERROR"
                status = jsonify(res.json())
        except:
            state = "ERROR"
            status = f"Cannot reach ODK server at {odk['url']}"
        # post it on the task
        # retrieve file contents (should only contain "images" but checking for all keys to make sure)
        if state != "ERROR":
            fields = {"images": (att["name"], res.content, "images/jpg")}
            try:
                res = odm_requests.post_upload(fields=fields, **odm)
                if res.status_code == 200:
                    status = f"{att['name']} uploaded..."
                else:
                    state = "ERROR"
                    status = jsonify(res.json())
            except:
                state = "ERROR"
                status = f"Cannot reach ODM server at {odm['url']}"
        print(f"State is: {status}")
        self.update_state(
            state=state,
            meta={
                'current': n,
                'total': len(submissions),
                'status': status
            }
        )
        return

    print("Running job as a Thread!")
    for n, sub in enumerate(submissions):
        # retrieve all attachments
        attachments = odk_requests.attachment_list(instanceId=sub["instanceId"], **odk)
        for att in attachments.json():
            transfer(att)
    # finally return the success status
    return {
        'current': len(submissions),
        'total': len(submissions),
        'status': 'Upload completed!',
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

@mesh_api.route("/api/mesh/<id>", methods=["GET"])
@login_required
def get_mesh(id):
    """
    API endpoint for getting specific mesh available to currently logged in user

    :return:
    """
    mesh = Mesh.query.filter_by(id=id).filter(Mesh.user_id == current_user.id).first()
    return jsonify(mesh.to_dict())


@mesh_api.route("/api/mesh/<id>", methods=["POST"])
@login_required
def post_attachment(id):
    try:
        mesh = Mesh.query.filter_by(id=id).filter(Mesh.user_id == current_user.id).one()
    except:
        return jsonify("Access denied"), 403
    content = request.get_json()
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
def submit_upload(id):
    try:
        mesh = Mesh.query.filter_by(id=id).filter(Mesh.user_id == current_user.id).one()
    except:
        return jsonify("Access denied"), 403
    # retrieve the relevant odk and odm server and project details
    # poll for the status of the last upload done, if status does not exist or is completed, then go, otherwise flash
    if mesh.current_task:
        res = taskstatus(mesh.current_task)
        print(res.json)
        if (res.json["state"] == "PROGRESS" or res.json["state"] == "PENDING"):
            # retrieve content
            return "Too many requests on your account, please wait for your uploads to complete", 429

    # retrieve content
    content = request.get_json()
    submissions = content["submissions"]
    odm_task = content["odm_task"]  # needs to be specified by the user on front end, therefore a loose item
    odk_formId = content["odk_formId"]
    odk_server = mesh.odkproject.odk
    odmproject = mesh.odmproject
    odm_server = odmproject.odm  # odm server record
    odm = {
        "base_url": odm_server.url,
        "token": odm_server.token,
        "project_id": mesh.odmproject.remote_id,
        "task_id": odm_task
    }
    odk = {
        "base_url": odk_server.url,
        "aut": (odk_server.user, odk_server.password),
        "projectId": mesh.odkproject.remote_id,
        "formId": odk_formId
    }

    task = odk2odm.apply_async(submissions=submissions, odk=odk, odm=odm)
    # odk
    #
    # task = test_job.apply_async()
    mesh.current_task = task.id
    db.commit()
    print(task.id)
    return f"Task {task.id} submitted", 202

@mesh_api.route("/api/mesh/test", methods=["GET"])
@login_required
def mesh_test():
    task = test_job.apply_async()
    print(task.id)
    return jsonify({}), 202, {'Location': url_for('mesh_api.taskstatus',
                                                  task_id=task.id)}

# status api request
@mesh_api.route("/api/status/<task_id>")
def taskstatus(task_id):
    task = odk2odm.AsyncResult(task_id)
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