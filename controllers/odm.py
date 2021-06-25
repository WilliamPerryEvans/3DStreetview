import json
from flask import Blueprint, jsonify, request, flash, url_for, redirect
import requests
from models.odmconfig import Odmconfig
from flask import current_app
# API components that retrieve or download data from database for use on front end
odm_api = Blueprint("odm_api", __name__)

@odm_api.route("/api/odm/create_project/<id>/<name>", methods=["POST"])
def create_project(id, name):
    """
    API endpoint for getting list of devices and states of devices

    :return:
    """
    # retrieve config from database
    odmconfig = Odmconfig.query.get(id)
    # request token
    url = f"{odmconfig.host}:{odmconfig.port}/api/token-auth/"
    res = requests.post(
        url,
        data={
            "username": odmconfig.user,
            "password": odmconfig.password
        }
    )
    if res.status_code == 403:
        current_app.logger.error(f"You do not have permissions to access {url}")
        return
    elif res.status_code != 200:
        current_app.logger.error(f"{url} is not accessible or does not exist")
        return
    token = res.json()['token']
    url = f"{odmconfig.host}:{odmconfig.port}/api/projects/"
    res = requests.post(
        url,
        headers={'Authorization': 'JWT {}'.format(token)},
        data={'name': name}
    )
    if res.status_code == 403:
        current_app.logger.error(f"You do not have permissions to access {url}")
        return
    current_app.logger.info(f"Project {name} successfully added to ODM server {odmconfig}")
