import os
from cryptography.fernet import Fernet
from sqlalchemy import Integer, ForeignKey, String, Column, event, LargeBinary
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from streetview.models.base import Base

class Odk(Base, SerializerMixin):
    """
    ODK Central API access configuration.
    """
    __tablename__ = "odk"
    id = Column(Integer, primary_key=True)
    # Odk server config are entirely tied to a given user
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=443)  #
    user = Column(String, default=None)  # user of ODK server
    password_encrypt = Column(LargeBinary, default=None)  # encrypted password
    timeout = Column(Integer, default=30)  # timeout in seconds
    app_user = relationship("User")  # user of 3DSV


    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

    @property
    def url(self):
        """
        get a base url from the server config record
        :return: url (str)
        """
        return f"{self.host}:{self.port}"

    @property
    def password(self):
        """
        decrypt password
        :return: decrypted password
        """
        f = Fernet(os.getenv("FERNET_KEY"))  # prepare encryption
        return f.decrypt(self.password_encrypt).decode()

@event.listens_for(Odk, "before_insert")
@event.listens_for(Odk, "before_update")
def receive_before_insert(mapper, connection, target):
    """
    Encrypt password before submitting
    :param mapper:
    :param connection:
    :param target: Odm model
    """
    f = Fernet(os.getenv("FERNET_KEY"))  # prepare encryption
    target.password_encrypt = f.encrypt(target.password_encrypt.encode())  # encrypt password with key

