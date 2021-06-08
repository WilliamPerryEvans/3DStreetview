import os
import enum
from sqlalchemy import Integer, ForeignKey, String, Column, Enum, Float, event
from sqlalchemy_serializer import SerializerMixin
from models.base import Base
from models.elements.unzipmesh import unzipmesh

class MeshStatus(enum.Enum):
    INACTIVE = 0
    ACTIVE = 1

class Mesh(Base, SerializerMixin):
    __tablename__ = "mesh"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    centroid_x = Column(Float, nullable=False)
    centroid_y = Column(Float, nullable=False)
    status = Column(Enum(MeshStatus), default=MeshStatus.INACTIVE)

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

@event.listens_for(Mesh, "after_insert")
@event.listens_for(Mesh, "after_update")
def receive_after_update(mapper, connection, target):
    src_path = "mesh"
    trg_path = f"static/{src_path}/{target.id}"
    file_name = os.path.join(src_path, target.file_name)
    if not(os.path.isfile(file_name)):
        raise IOError(f"File {file_name} does not exist")
    unzipmesh(file_name, trg_path=trg_path, mesh_name="unity")
