from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import db_configuration

engine = create_engine(db_configuration, client_encoding='utf8')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()


class PlotKeyword(Base):
    __tablename__ = 'tmdb_plot_keywords'
    id = Column(Integer, primary_key=True)
    keyword = Column(String(500), unique=True)

    def __str__(self):
        return self.keyword


class MoviesKeywords(Base):
    __tablename__ = 'tmdb_plot_keywords_connecction'
    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('tmdb_plot_keywords.id'))
    movie_id = Column(Integer, ForeignKey('movies_tmdb.id'))


class Movies_tmdb(Base):
    __tablename__ = 'movies_tmdb'
    id = Column(Integer, primary_key=True)
    title = Column(String(140), unique=True)
    genre = Column(String(100))

    def __str__(self):
        return self.title


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
