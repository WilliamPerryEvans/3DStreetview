import os
import enum
from sqlalchemy import Integer, ForeignKey, String, Column, Enum, Float, event
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base
from models.elements.unzipmesh import unzipmesh

class MeshStatus(enum.Enum):
    """
    Status of mesh should change upon callbacks from OpenDroneMap
    """
    NEW = 0  # new mesh instantiated, not ready for processing
    READY = 1  # mesh can be processed as several (minimum xxx) files are available to process
    PROCESSING = 2  # mesh is being processed on ODM server, callbacks on status being received
    FINISHED = 3  # mesh is finished and ready for display in meshraider
    ERROR = 3  # mesh is finished and ready for display in meshraider

class Mesh(Base, SerializerMixin):
    """
    Mesh including relationships with ODK attachments and ODM processing. Mesh always belongs to a project which may
    include several meshes.
    Process envisaged is:
    - User makes a project
    per project:
        - user makes a mesh
        per mesh:
            - user selects files from ODK server(s)/project(s)/form(s) to be included in mesh
            - user selects an ODM project for mesh processing
            - actions of user and callbacks are reflected on status of mesh
    """
    __tablename__ = "mesh"
    id = Column(Integer, primary_key=True)
    # project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    odmproject_id = Column(Integer, ForeignKey("odmproject.id"))  # also nullable in case a user simply wants to upload a mesh
    odkproject_id = Column(Integer, ForeignKey("odkproject.id"))  # also nullable in case a user simply wants to upload a mesh
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    zipfile = Column(String)  # if a .zip file containing a mesh is supplied, then this is unzipped immediately.
    status = Column(Enum(MeshStatus), default=MeshStatus.NEW)
    # project = relationship("Project")
    odmproject = relationship("Odmproject")
    odkproject = relationship("Odkproject")

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

@event.listens_for(Mesh, "after_insert")
@event.listens_for(Mesh, "after_update")
def receive_after_update(mapper, connection, target):
    """
    event listener, to be executed when a zipfile is provided for upload
    """
    src_path = "mesh"
    trg_path = f"static/{src_path}/{target.id}"
    if target.zipfile is not None:
        zipfile = os.path.join(src_path, target.zipfile)
        if not(os.path.isfile(zipfile)):
            raise IOError(f"File {zipfile} does not exist")
        unzipmesh(zipfile, trg_path=trg_path, mesh_name="unity")
        # no processing needed, so set Mesh status to finished immediately
        print("Set Mesh status to 'Finished'")
        target.status = 3

