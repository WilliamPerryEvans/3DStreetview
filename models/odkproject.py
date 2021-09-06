from sqlalchemy import Integer, ForeignKey, String, Column, event
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship

from models.base import Base
from models.odk import Odk
from odk2odm import odk_requests

import os
import requests

# here, add any ODK forms that need to be added to a new ODK project when created within the UI
odk_forms = ["static/forms/3DStreetView_main.xlsx", "static/forms/3DStreetView_fill.xlsx"]

class Odkproject(Base, SerializerMixin):
    """
    Association table, for associating an ODK project to a Mesh record. Currently assumed to be a
    one-to-one relationship.
    The full table of projects available for association should be retrieved with the ODK API
    """
    __tablename__ = "odkproject"
    serialize_only = ('id', 'odk_id', 'remote_id')
    id = Column(Integer, primary_key=True)  # id of local ODK project reference
    odk_id = Column(Integer, ForeignKey("odk.id"), nullable=False)  # id of odk server config
    remote_id = Column(Integer, nullable=False)  # id as known on remote server
    odk = relationship("Odk")

    @property
    def app_users(self):
        url = f'{self.odk.url}/v1/projects/{self.remote_id}/app-users'
        return requests.get(url, auth=(self.odk.user, self.odk.password)).json()

    @property
    def project(self):
        return odk_requests.project(self.odk.url, aut=(self.odk.user, self.odk.password), projectId=self.remote_id).json()

    def __str__(self):
        return "{}".format(self.remote_id)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

@event.listens_for(Odkproject, "after_insert")
def receive_after_insert(mapper, connection, target):
    """
    Upload forms into the prepared Odkproject on the server

    :param mapper:
    :param connection:
    :param target:
    """
    # odk relationship not yet available so query that from db
    odk = Odk.query.get(target.odk_id)
    base_url = odk.url
    aut = (odk.user, odk.password)
    projectId = target.remote_id
    responses = []
    for odk_form in odk_forms:
        with open(odk_form, "rb") as f:
            data = f.read()
        name = os.path.split(odk_form)[-1].split(".")[0]
        # TODO: finish
        res = odk_requests.create_form(base_url, aut, projectId, name, data)
        responses.append(res.json())
    res = odk_requests.give_access_app_users(base_url, aut, projectId)
    return responses, 200