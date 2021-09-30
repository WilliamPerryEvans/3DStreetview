import os
from flask import Blueprint, jsonify, request
from flask_security import login_required, current_user
from streetview.models.mesh import Mesh
from streetview.models import db
from odk2odm import odk_requests
from odk2odm import odm_requests
# API components that retrieve or download data from database for use on front end
from cryptography.fernet import Fernet

mesh_api = Blueprint("mesh_api", __name__)

from streetview import celery

@celery.task(bind=True)
def odk2odm(self, submissions=[], odk={}, odm={}):
    """
    retrieves from ODK and transfers to ODM, all attachments from list of submissions in ODK project/form
    celery task, so supposed to run as a background task
    :param self: celery object
    :param submissions: list of submissions retrieved from ODK server and form
    :param odk: dictionary with server settings for odk, including url, auth tuple, projectId and formId
    :param odm: dictionary with server settings for odm, including url, token, project_id and task_id
    :return:
    """
    def transfer(att, state="PROGRESS"):
        """
        subroutine to transfer one file, function returns None always
        :param att: attachment details from odk server
        :param state: celery state string
        :return:
        """
        if att["exists"]:
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
            print(f"Transfer of {att['name']}")
            res = odk_requests.attachment(instanceId=sub["instanceId"], filename=att["name"], **odk)
            try:
                if res.status_code != 200:
                    # something went wrong, so report that
                    raise IOError(res.json())
            except:
                raise IOError(f"Cannot reach ODK server at {odk['url']}")
            # post it on the task
            # retrieve file contents (should only contain "images" but checking for all keys to make sure)
            fields = {"images": (att["name"], res.content, "images/jpg")}
            try:
                res = odm_requests.post_upload(fields=fields, **odm)
                if res.status_code == 200:
                    status = f"{att['name']} uploaded..."
                else:
                    raise IOError(res.json())
            except:
                raise IOError(f"Cannot reach ODM server at {odm['url']}")
            self.update_state(
                state=state,
                meta={
                    'current': n,
                    'total': len(submissions),
                    'status': status
                }
            )
        else:
            print(f"File {att['name']} is missing in ODK submission {sub['instanceId']}")
        return

    # setup authentication for both server
    f = Fernet(os.getenv("FERNET_KEY"))  # prepare decryption
    odk["aut"] = (odk["user"], f.decrypt(odk["password_encrypt"].encode()).decode())
    del odk["user"], odk["password_encrypt"]
    res = odm_requests.get_token_auth(
        odm["base_url"],
        odm["user"],
        f.decrypt(odm["password_encrypt"].encode()).decode()
    )
    print(f"failed login is: {res.status_code}")
    if res.status_code == 400:
        # login failed so return an error
        raise PermissionError("Access denied to ODM server")

    odm["token"] = res.json()["token"]
    del odm["user"], odm["password_encrypt"]

    print(f"odk conf: {odk}")
    print(f"odm conf: {odm}")
    print(f"Submissions: {submissions}")
    for n, sub in enumerate(submissions):
        # retrieve all attachments
        print(f"Treating submission {sub['instanceId']}")
        attachments = odk_requests.attachment_list(instanceId=sub["instanceId"], **odk)
        print(f"Attachments {attachments.json()}")
        if attachments.status_code == 401:
            raise PermissionError("Access denied to ODK server")
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
    """
    Any request in this controller can only be performed by logged in users
    :return: response
    """
    if current_user.is_anonymous:
        return jsonify("Forbidden"), 401

@mesh_api.route("/api/mesh/", methods=["GET"])
@login_required
def get_meshes():
    """
    API endpoint for getting list of meshes available to currently logged in user

    :return: response
    """
    meshes = Mesh.query.filter_by(id=id).filter(Mesh.user_id == current_user.id).all()
    return jsonify([d.to_dict() for d in meshes])

@mesh_api.route("/api/mesh/<id>", methods=["GET"])
@login_required
def get_mesh(id):
    """
    API endpoint for getting specific mesh available to currently logged in user

    :return: response
    """
    mesh = Mesh.query.filter_by(id=id).filter(Mesh.user_id == current_user.id).first()
    return jsonify(mesh.to_dict())


@mesh_api.route("/api/mesh/<id>", methods=["POST"])
@login_required
def post_attachment(id):
    """
    Post attachment in ODM project and task belonging to mesh with id <id>
    The task_id of the ODM project must be contained in the request data, as json with field "odm_kwargs"
    The projectId and formId of the ODK project must be contained in the request data, as json with field "odk_kwargs"
    :param id: id of mesh
    :return: response
    """
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
    """
    Sumbit an upload task for celery workers. odm and odk details must be provided in json content of request

    :param id: id of mesh that task belongs to
    :return: response
    """
    try:
        mesh = Mesh.query.filter_by(id=id).filter(Mesh.user_id == current_user.id).one()
    except:
        return jsonify("Access denied"), 403
    # retrieve the relevant odk and odm server and project details
    # poll for the status of the last upload done, if status does not exist or is completed, then go, otherwise flash
    if mesh.current_task:
        res = taskstatus(mesh.current_task)
        if (res.json["state"] == "PROGRESS" or res.json["state"] == "PENDING"):
            # retrieve content
            return "Too many requests on your account, please wait for your uploads to complete", 429

    # retrieve content
    content = request.get_json()
    submissions = content["submissions"]
    print(f"submissions: {submissions}")
    odm_task = content["odm_task"]  # needs to be specified by the user on front end, therefore a loose item
    odk_formId = content["odk_formId"]
    odk_server = mesh.odkproject.odk
    odmproject = mesh.odmproject
    odm_server = odmproject.odm  # odm server record
    odm = {
        "base_url": odm_server.url,
        "user": odm_server.user,
        "password_encrypt": odm_server.password_encrypt.decode(),
        "token": odm_server.token,
        "project_id": mesh.odmproject.remote_id,
        "task_id": odm_task
    }
    odk = {
        "base_url": odk_server.url,
        "user": odk_server.user,
        "password_encrypt": odk_server.password_encrypt.decode(),
        "aut": (odk_server.user, odk_server.password),
        "projectId": mesh.odkproject.remote_id,
        "formId": odk_formId
    }

    task = odk2odm.apply_async(kwargs={"submissions": submissions, "odk": odk, "odm": odm})
    # odk
    #
    # task = test_job.apply_async()
    mesh.current_task = task.id
    db.commit()
    print(task.id)
    return f"Task {task.id} submitted", 202

# status api request
@mesh_api.route("/api/status/<task_id>")
def taskstatus(task_id):
    """
    API route for status of a celery task
    :param task_id: uuid of celery task
    :return: response
    """
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