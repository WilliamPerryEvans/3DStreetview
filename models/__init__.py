from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from models.base import Base
# TODO: Remove hardcoded connection URI.
engine = create_engine("postgresql://streetview:zanzibar@localhost:5432/streetview", pool_size=50, pool_recycle=3600, pool_pre_ping=0, max_overflow=0)

from models import user
# from models import project
from models import odk
from models import odm
from models import odmproject
from models import odkproject
from models import mesh
# TODO: Persistent database by removing drop all once DB models are stable..
# Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
db = scoped_session(DBSession)
Base.query = db.query_property()
