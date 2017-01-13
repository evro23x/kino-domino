from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import db_configuration

engine = create_engine(db_configuration, client_encoding='utf8')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()


class MetroStations(Base):
    __tablename__ = 'metro_stations'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True)
    latitude = Column(Float)
    longitude = Column(Float)
    district = Column(String(50))
    movie_theaters = relationship('MovieTheaters', backref='theaters')

    def __init__(self, title=None, latitude=None, longitude=None):
        self.title = title
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '<{} metro station>'.format(self.title)


class MovieTheaters(Base):
    __tablename__ = 'movie_theaters'
    id = Column(Integer, primary_key=True)
    metro_id = Column(Integer, ForeignKey('metro_stations.id'))
    title = Column(String(140))
    adress = Column(String(500))
    description = Column(Text)
    phone = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    time_slots = relationship('TimeSlots', backref='time_slots1')

    def __init__(self, metro_id, title=None, adress=None, latitude=None, longitude=None,  description=None,  phone=None):
        self.metro_id = metro_id
        self.title = title
        self.adress = adress
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        self.phone = phone

    def __repr__(self):
        return '<{} Movie_theater>'.format(self.title)


class TimeSlots(Base):
    __tablename__ = "time_slots"
    id = Column(Integer, primary_key=True)
    movie_theaters_id = Column(Integer, ForeignKey('movie_theaters.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    movie_formats_id = Column(Integer, ForeignKey('movie_formats.id'))
    time = Column(DateTime)
    cost = Column(Float)

    def __init__(self, movie_theaters_id=None, movie_id=None, time=None, cost=None):
        self.movie_theaters_id = movie_theaters_id
        self.movie_id = movie_id
        self.time = time
        # self.cost = cost

    def __repr__(self):
        return '< {} at {} in {} >'.format(self.movie_id, self.time, self.movie_theaters_id)


class Movies(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    title = Column(String(120))
    description = Column(Text)
    duraction = Column(String(120))
    start_date = Column(String(120))
    rating = Column(String(120))
    time_slots = relationship('TimeSlots', backref='time_slots2')

    def __init__(self, title=None):
        self.title = title

    def __repr__(self):
        return '<{}>'.format(self.title)


class MovieFormats(Base):
    __tablename__ = "movie_formats"
    id = Column(Integer, primary_key=True)
    title = Column(String(120))
    time_slots = relationship('TimeSlots', backref='time_slots3')

    def __init__(self, title=None):
        self.title = title

    def __repr__(self):
        return '<{}>'.format(self.title)


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
