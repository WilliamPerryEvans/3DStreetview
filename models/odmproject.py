from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base

class Odmproject(Base, SerializerMixin):
    """
    Association table, for associating an ODM project to a Mesh record. Currently assumed to be a
    one-to-one relationship.
    The full table of projects available for association should be retrieved with the ODM API
    """
    __tablename__ = "odmproject"
    id = Column(Integer, primary_key=True)
    odm_id = Column(Integer, ForeignKey("odm.id"), nullable=False)
    name = Column(String, nullable=False)
    odm = relationship("Odm")

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())
