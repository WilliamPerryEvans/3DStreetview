import os
import shutil
from sqlalchemy import Integer, ForeignKey, String, Column, event
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from streetview.models.base import Base
from streetview.models.elements.unzipmesh import unzipmesh

class Game(Base, SerializerMixin):
    """
    Game model for managing and exposing game files
    """
    __tablename__ = "game"
    id = Column(Integer, primary_key=True)
    mesh_id = Column(Integer, ForeignKey("mesh.id"), nullable=False)
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
    trg_path = f"streetview/static/{src_path}/{target.id}"
    if not(os.path.isdir(trg_path)):
        os.makedirs(trg_path)
    if target.zipfile is not None:
        zipfile = os.path.join(src_path, target.zipfile)
        if not(os.path.isfile(zipfile)):
            raise IOError(f"File {zipfile} does not exist")
        unzipmesh(zipfile, trg_path=trg_path, mesh_name="unity")
        # after unzipping, throw away the .zip file
        os.remove(zipfile)

@event.listens_for(Game, "after_delete")
def receive_after_update(mapper, connection, target):
    """
    event listener, to be executed when a Game is deleted
    Also delete the associated folder coontaining the unity game files

    """
    trg_path = f"streetview/static/mesh/{target.id}"
    if os.path.isdir(trg_path):
        # remove entire folder
        shutil.rmtree(trg_path)
