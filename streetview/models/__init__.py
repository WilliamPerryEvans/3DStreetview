import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from streetview.models.base import Base

postgres_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_SERVER')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(postgres_url, pool_size=50, pool_recycle=3600, pool_pre_ping=0, max_overflow=0)

from streetview.models import odk

# TODO: Persistent database by removing drop all once DB models are stable..
# Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
db = scoped_session(DBSession)
Base.query = db.query_property()
