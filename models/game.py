import os
import enum
from sqlalchemy import Integer, ForeignKey, String, Column, Enum, Float, event
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base
from models.elements.unzipmesh import unzipmesh

class Game(Base, SerializerMixin):
    """
    TODO Describe data model
    """
    __tablename__ = "game"
    id = Column(Integer, primary_key=True)
    mesh_id = Column(Integer, ForeignKey("mesh.id"))
    name = Column(String, nullable=False)
    zipfile = Column(String)  # if a .zip file containing a mesh is supplied, then this is unzipped immediately.
    mesh = relationship("Mesh")

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

