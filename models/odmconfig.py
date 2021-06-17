import os
import enum
from sqlalchemy import Integer, ForeignKey, String, Column, Enum, Float, event
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base

class Odmconfig(Base, SerializerMixin):
    """
    NodeODM API access configuration. Adapted from https://pyodm.readthedocs.io/en/latest/
    """
    __tablename__ = "odmconfig"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=3000)  #
    token = Column(String, default=None)  # token string to allow login
    timeout = Column(Integer, default=30)  # timeout in seconds

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

