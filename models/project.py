from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base

class Project(Base, SerializerMixin):
    """
    Base table with projects
    """
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("site.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    site = relationship("Site")

    def __str__(self):
        return "{} at {}".format(self.name, self.site)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())
