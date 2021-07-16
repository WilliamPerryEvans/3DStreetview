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


@event.listens_for(Game, "after_insert")
@event.listens_for(Game, "after_update")
def receive_after_update(mapper, connection, target):
    """
    event listener, to be executed when a zipfile is provided for upload
    """
    src_path = "mesh"
    trg_path = f"static/{src_path}/{target.id}"
    if not(os.path.isdir(trg_path)):
        os.makedirs(trg_path)
    if target.zipfile is not None:
        zipfile = os.path.join(src_path, target.zipfile)
        if not(os.path.isfile(zipfile)):
            raise IOError(f"File {zipfile} does not exist")
        unzipmesh(zipfile, trg_path=trg_path, mesh_name="unity")

