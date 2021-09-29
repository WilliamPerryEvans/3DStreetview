import enum
from sqlalchemy import Integer, ForeignKey, String, Column, Enum, Float, event
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from streetview.models.base import Base
from streetview.models.odkproject import Odkproject
from streetview.models.odmproject import Odmproject


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
    Mesh including relationships with ODK attachments and ODM processing.
    Mesh projects are connected to users
    """
    __tablename__ = "mesh"
    serialize_only = ('id', 'user_id', 'odmproject_id', 'odkproject_id', 'name', 'latitude', 'longitude', 'status', 'current_task', 'odmproject', 'odkproject')
    id = Column(Integer, primary_key=True)
    # Mesh projects are entirely tied to a given user
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    odmproject_id = Column(Integer, ForeignKey("odmproject.id"))  # also nullable in case a user simply wants to upload a mesh
    odkproject_id = Column(Integer, ForeignKey("odkproject.id"))  # also nullable in case a user simply wants to upload a mesh
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    # zipfile = Column(String)  # if a .zip file containing a mesh is supplied, then this is unzipped immediately.
    status = Column(Enum(MeshStatus), default=MeshStatus.NEW)
    current_task = Column(String)
    # project = relationship("Project")
    odmproject = relationship("Odmproject")
    odkproject = relationship("Odkproject")
    user = relationship("User")

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

@event.listens_for(Mesh, 'after_delete')
def receive_after_update(mapper, connection, target):
    """
    event listener, to be executed when a Mesh is deleted
    Also delete the associated odm project and odk project from local dbase

    """
    Odkproject.query.filter(Odkproject.id == target.odkproject_id).delete()
    Odmproject.query.filter(Odmproject.id == target.odmproject_id).delete()

