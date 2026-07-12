"""SQLite and SQLAlchemy session setup."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////data/cifraclub.db")
Base = declarative_base()
engine = None
Session = None


def configure_database(url=None):
    """Configure the engine, primarily allowing isolated test databases."""
    global DATABASE_URL, engine, Session
    DATABASE_URL = url or DATABASE_URL
    options = {"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}
    engine = create_engine(DATABASE_URL, **options)
    Session = scoped_session(sessionmaker(bind=engine))


def init_db():
    if engine is None:
        configure_database()
    Base.metadata.create_all(bind=engine)


def get_session():
    init_db()
    return Session()


configure_database()
