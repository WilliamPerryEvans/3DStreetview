import json
from flask import Blueprint, jsonify, request, flash, url_for, redirect
import requests
from models.odmconfig import Odmconfig
from flask import current_app
# API components that retrieve or download data from database for use on front end
odm_api = Blueprint("odm_api", __name__)

@odm_api.route("/api/odm/<id>/token-auth", methods=["GET"])
def get_token(id):
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
    API endpoint for getting list of devices and states of devices

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
    API endpoint for getting list of devices and states of devices

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
        token = res.json()['token']
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

#
#
#
# images = [
#     ('images', ('image1.jpg', open('image1.jpg', 'rb'), 'image/jpg')),
#     ('images', ('image2.jpg', open('image2.jpg', 'rb'), 'image/jpg')),
#     # ...
# ]
# options = json.dumps([
#     {'name': "orthophoto-resolution", 'value': 24}
# ])
#
# res = requests.post('http://localhost:8000/api/projects/{}/tasks/'.format(project_id),
#             headers={'Authorization': 'JWT {}'.format(token)},
#             files=images,
#             data={
#                 'options': options
#             }).json()
#
# task_id = res['id']