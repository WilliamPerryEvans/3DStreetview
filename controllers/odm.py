import json
from flask import Blueprint, jsonify, request, flash, url_for, redirect
import requests
from models.odmconfig import Odmconfig
from flask import current_app
# API components that retrieve or download data from database for use on front end
odm_api = Blueprint("odm_api", __name__)

@odm_api.route("/api/odm/<id>/token-auth", methods=["GET"])
def get_token(id):
    """
    Get a token for access to ODM server
    :param id: odm configuration id
    :return:
    """
    # retrieve config from database
    odmconfig = Odmconfig.query.get(id)
    # request token
    url = f"{odmconfig.host}:{odmconfig.port}/api/token-auth/"
    try:
        res = requests.post(
            url,
            data={
                "username": odmconfig.user,
                "password": odmconfig.password
            }
        )
        if res.status_code == 403:
            current_app.logger.error(f"You do not have permissions to access {url}")
            return res.json(), res.status_code
        elif res.status_code != 200:
            current_app.logger.error(f"{url} is not accessible or does not exist")
            return res.json(), res.status_code
        return res.json()['token'], 200
    except:
        return f"Page {url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects", methods=["GET"])
def list_projects(id):
    """
    API endpoint for getting list of ODM projects from odm config
    :param id: odm configuration id
    :return:
    """
    # retrieve config from database
    odmconfig = Odmconfig.query.get(id)
    # request token
    token = get_token(id)[0]
    url = f"{odmconfig.host}:{odmconfig.port}/api/token-auth/"
    try:
        url = f"{odmconfig.host}:{odmconfig.port}/api/projects"
        res = requests.get(
            url,
            headers={'Authorization': 'JWT {}'.format(token)},
        )
        if res.status_code == 403:
            current_app.logger.error(f"You do not have permissions to access {url}")
            return res.json(), res.status_code
        current_app.logger.info(f"Project list successfully retrieved from ODM server {odmconfig}")
        return jsonify(res.json())
    except:
        return f"Page {url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>", methods=["GET"])
def project(id, project_id):
    """
    API endpoint for getting details of project

    :return:
    """
    # retrieve config from database
    odmconfig = Odmconfig.query.get(id)
    # request token
    token = get_token(id)[0]
    try:
        url = f"{odmconfig.host}:{odmconfig.port}/api/projects/{project_id}"
        res = requests.get(
            url,
            headers={'Authorization': 'JWT {}'.format(token)},
        )
        if res.status_code == 403:
            current_app.logger.error(f"You do not have permissions to access {url}")
            return res.json(), res.status_code
        current_app.logger.info(f"Project details successfully retrieved from ODM server {odmconfig}")
        return jsonify(res.json())
    except:
        return f"Page {url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/", methods=["POST"])
def create_project(id):
    """
    API endpoint for getting list of devices and states of devices

    :return:
    """
    # retrieve config from database
    odmconfig = Odmconfig.query.get(id)
    # create data to pass to request
    content = request.get_json()
    # request token
    token = get_token(id)[0]
    try:
        url = f"{odmconfig.host}:{odmconfig.port}/api/projects/"
        res = requests.post(
            url,
            headers={'Authorization': 'JWT {}'.format(token)},
            data=content
        )
        if res.status_code == 403:
            current_app.logger.error(f"You do not have permissions to access {url}")
            return res.json(), res.status_code
        current_app.logger.info(f"Project successfully added to ODM server {odmconfig}")
        return jsonify(res.json())
    except:
        return f"Page {url} does not exist", 404


@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>", methods=["GET"])
def task(id, project_id, task_id):
    """
    API endpoint for getting details of task within project

    :return:
    """
    # retrieve config from database
    odmconfig = Odmconfig.query.get(id)
    # request token
    token = get_token(id)[0]
    try:
        url = f"{odmconfig.host}:{odmconfig.port}/api/projects/{project_id}/tasks/{task_id}/"
        res = requests.get(
            url,
            headers={'Authorization': 'JWT {}'.format(token)},
        )
        if res.status_code == 403:
            current_app.logger.error(f"You do not have permissions to access {url}")
            return res.json(), res.status_code
        current_app.logger.info(f"Task details successfully retrieved from ODM server {odmconfig}")
        return jsonify(res.json())
    except:
        return f"Page {url} does not exist", 404



@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/", methods=["POST"])
def create_task(id, project_id):
    # TODO: allow for passing of options from allowed list
    # get the odm config
    odmconfig = Odmconfig.query.get(id)
    token = get_token(id)[0]
    # retrieve requested data
    data = request.get_json()
    # make a new task, pass on data
    url = f"{odmconfig.host}:{odmconfig.port}/api/projects/{project_id}/tasks/"
    headers = {'Authorization': 'JWT {}'.format(token)}
    res = requests.post(
        url,
        headers=headers,
        data=data,
    )
    return jsonify(res.json())

@odm_api.route("/api/odm/<id>/projects/<project_id>/tasks/<task_id>/upload/", methods=["POST"])
def upload(id, project_id, task_id):
    # retrieve config from database
    odmconfig = Odmconfig.query.get(id)
    token = get_token(id)[0]
    headers = {'Authorization': 'JWT {}'.format(token)}
    from requests_file import FileAdapter
    s = requests.Session()
    s.mount('file://', FileAdapter())
    # create data to pass to request
    content = request.get_json()
    # request token
    # TODO: get_json with all image information
    folder = "/home/hcwinsemius/tmp/photos"
    import glob, os
    imgs = glob.glob(os.path.join(folder, "*.JPG"))
    index = 0
    options = json.dumps([
        {'name': "orthophoto-resolution", 'value': 24}
    ])

    images = [
        ('images', (os.path.split(img)[-1], None, 'image/jpg')) for img in imgs
    ]
    headers["Content-type"] = 'multipart/form-data; boundary="XXXXX"'  #
    for n, img in enumerate(imgs):
        c = s.get("file://" + img, stream=True).content
        images = [('images', (os.path.split(img)[-1], c, 'image/jpg'))]
        # images[n] = ('images', (os.path.split(img)[-1], c, 'image/jpg'))
        # if n > 0:
        #     images[n-1] = ('images', (images[n-1][1], None, 'image/jpg'))
        # offset = index + len(c)
        # if n < len(imgs)-1:
        #     length = offset
        #     partial = True
        # else:
        #     length = offset - 1
        #     partial = False
        # headers["Content-Range"] = f'bytes {index}-{offset-1}/{length}'
        #
        # index = offset
        url = f"{odmconfig.host}:{odmconfig.port}/api/projects/{project_id}/tasks/{task_id}/upload/"
        print(url)
        res = requests.post(
            url,
            headers=headers,
            data={
                images
                # "partial": True,
                # "files": images,
            },
            # files=images
        )
        print(res.json())

# except:
#     return f"Page {url} does not exist", 404
    return jsonify(res.json())

    # task_id = res['id']