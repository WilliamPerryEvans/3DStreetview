from sqlalchemy import (
    Integer,
    ForeignKey,
    String,
    Column,
    DateTime,
    Boolean,
    event
)
from sqlalchemy.orm import relationship, backref
from streetview.models.base import Base
from flask import request
from flask_security import UserMixin, RoleMixin
from flask_mail import Message


class RolesUsers(Base):
    __tablename__ = "roles_users"
    id = Column(Integer(), primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey("user.id"))
    role_id = Column("role_id", Integer(), ForeignKey("role.id"))


class Role(Base, RoleMixin):
    __tablename__ = "role"
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    def __str__(self):
        return "{}".format(self.description)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


class User(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255))
    password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship(
        "Role", secondary="roles_users", backref=backref("users", lazy="dynamic")
    )

    def __str__(self):
        return "{}".format(self.email)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


@event.listens_for(User, "after_update")
def receive_after_update(mapper, connection, target):
    """
    event listener, to be executed when the active status was changed
    """
    if target.active:
        # apparently user is set to active, so send out an email
        from streetview.__init__ import app, mail
        if app.config["SECURITY_SEND_REGISTER_EMAIL"]:
            msg = Message(
                f"Welcome to 3DStreetView",
                recipients=[target.email]
            )
            msg.body = f"We have activated your account and you can now browse to {request.url_root} to start creating immersive meshes with our platform.\n If you have questions or feedback, please contact us at info@rainbowsensing.com."
            mail.send(msg)

