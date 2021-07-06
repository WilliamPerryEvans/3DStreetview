from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base

class Odkproject(Base, SerializerMixin):
    """
    Association table, for associating an ODK project to a Mesh record. Currently assumed to be a
    one-to-one relationship.
    The full table of projects available for association should be retrieved with the ODK API
    """
    __tablename__ = "odkproject"
    id = Column(Integer, primary_key=True)
    odk_id = Column(Integer, ForeignKey("odk.id"), nullable=False)
    name = Column(String, nullable=False)
    odk = relationship("Odk")

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())
