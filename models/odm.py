import os
import enum
from sqlalchemy import Integer, ForeignKey, String, Column, Enum, Float, event
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base
from odk2odm import odm_requests

class Odm(Base, SerializerMixin):
    """
    WebODM API access configuration
    """
    __tablename__ = "odm"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=8000)  #
    user = Column(String, default=None)  # token string to allow login
    password = Column(String, default=None)  # token string to allow login
    timeout = Column(Integer, default=30)  # timeout in seconds

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

    @property
    def url(self):
        """
        get a base url from the server config record
        :return: url (str)
        """
        return f"{self.host}:{self.port}"

    @property
    def token(self):
        """
        get a token from server config
        :return:
        """
        res = odm_requests.token_auth(self.url, self.user, self.password)
        return res.json()['token']
