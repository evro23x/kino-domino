from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import db_configuration

engine = create_engine(db_configuration, client_encoding='utf8')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()


class Movies_tmdb(Base):
    __tablename__ = 'movies_tmdb'
    id = Column(Integer, primary_key=True)
    title = Column(String(140), unique=True)
    genre = Column(String(100))
    keyword1 = Column(String(50))
    keyword2 = Column(String(50))
    keyword3 = Column(String(50))
    keyword4 = Column(String(50))
    keyword5 = Column(String(50))
    keyword6 = Column(String(50))
    keyword7 = Column(String(50))
    keyword8 = Column(String(50))
    keyword9 = Column(String(50))
    keyword10 = Column(String(50))

    def __init__(self, title=None, genre=None, keyword1=None, keyword2=None, keyword3=None,
        keyword4=None, keyword5=None, keyword6=None, keyword7=None, keyword8=None, keyword9=None, 
        keyword10=None):
        self.title = title
        self.genre = genre
        self.keyword1 = keyword1
        self.keyword2 = keyword2
        self.keyword3 = keyword3
        self.keyword4 = keyword4
        self.keyword5 = keyword5
        self.keyword6 = keyword6
        self.keyword7 = keyword7
        self.keyword8 = keyword8
        self.keyword9 = keyword9
        self.keyword10 = keyword10

    def __repr__(self):
        return '<{}>'.format(self.title)


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)