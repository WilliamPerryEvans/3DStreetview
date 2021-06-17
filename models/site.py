from sqlalchemy import Integer, ForeignKey, String, Column, Float
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base

class Site(Base, SerializerMixin):
    """
    Base table with projects
    """
    __tablename__ = "site"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    def __str__(self):
        return "{} at {}".format(self.name, self.site)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())
