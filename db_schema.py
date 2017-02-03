from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import db_configuration

engine = create_engine(db_configuration, client_encoding='utf8')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
