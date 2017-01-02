from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///kino-domino.sqlite')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()


class Metro_stations(Base):
    __tablename__ = 'metro_stations'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    #posts = relationship('Post', backref='author')

    def __init__(self,name=None,latitude=None,longitude=None):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '<{} metro station>'.format(self.name)


class Movie_theaters(Base):
    __tablename__ = 'movie_theaters'
    id = Column(Integer, primary_key=True)
    name = Column(String(140))
    adress = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    time_slots = relationship('Time_slots', backref = 'time slot for movie')
    

    def __init__(self, name=None, adress=None, latitude=None, longitude=None):
        self.name = name
        self.adress = adress
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '<{} Movie_theater>'.format(self.name)


class Time_slots(Base):
    __tablename__ = "time_slots"
    id = Column(Integer, primary_key = True)
    movie_theater_id = Column(Integer, ForeignKey('movie_theaters.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    time = Column(DateTime)

    def __init__(self, time=None):
        self.time = time

    def __repr__(self):
        return '< {} at {} in {} >'.format(self.movie_id, self.time, movie_theater_id) 


class Movies(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key = True)
    name = Column(String(120))
    time_table = relationship('Time_slots', backref = 'movie')

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<{}>'.format(self.movie)


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)