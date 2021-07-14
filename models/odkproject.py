from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base
from odk2odm import odk_requests
import requests


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

