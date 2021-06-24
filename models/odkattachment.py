from sqlalchemy import Integer, ForeignKey, String, Column, Float
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base

class odkattachment(Base, SerializerMixin):
    """
    Association table, for associating records on an ODK server in a given project with given form to a Mesh
    record so that it is known which ODK files must be processed with ODM for a given Mesh. Currently assumed to be a
    many-to-one relationship.
    """
    __tablename__ = "odkattachment"
    id = Column(Integer, primary_key=True)
    odkconfig_id = Column(Integer, ForeignKey("odkconfig.id"), nullable=False)
    mesh_id = Column(Integer, ForeignKey("mesh.id"), nullable=False)
    location_x = Column(Float, nullable=False)
    location_y = Column(Float, nullable=False)
    odkprojectid = Column(String, nullable=False)
    odkformid = Column(String, nullable=False)  # TODO: figure out if we want to duplicate these in a table
    odkinstanceid = Column(Integer, nullable=False)  # TODO: figure out if we want to duplicate these in a table
    odkfilename = Column(String, nullable=False)  # TODO: figure out if we want to duplicate these in a table
    odkconfig = relationship("Odkconfig")
    mesh = relationship("Mesh")

    def __str__(self):
        return "{}".format(self.odkfilename)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())
