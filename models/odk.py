import os
import enum
from sqlalchemy import Integer, ForeignKey, String, Column, Enum, Float, event
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base

class Odk(Base, SerializerMixin):
    """
    ODK Central API access configuration.
    """
    __tablename__ = "odk"
    id = Column(Integer, primary_key=True)
    # Odk server config are entirely tied to a given user
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=3000)  #
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


