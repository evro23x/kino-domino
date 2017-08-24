from sqlalchemy import create_engine, Column, Integer, Float, String, Text, DateTime, ForeignKey, UniqueConstraint
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
    title = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    district = Column(String(50))
    created_time = Column(DateTime, default=0)
    movie_theaters = relationship('MovieTheaters', backref='theaters')

    def __init__(self, title=None, latitude=None, longitude=None):
        self.title = title
        self.latitude = latitude
        self.longitude = longitude


class MovieTheaters(Base):
    __tablename__ = 'movie_theaters'
    id = Column(Integer, primary_key=True)
    metro_id = Column(Integer, ForeignKey('metro_stations.id'))
    yandex_theater_id = Column(String(140))
    title = Column(String(140))
    address = Column(String(500))
    description = Column(Text)
    phone1 = Column(String(500))
    phone2 = Column(String(500))
    phone3 = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    time_slots = relationship('TimeSlots', backref='theater')
    created_time = Column(DateTime, default=0)

    def __init__(self, metro_id, yandex_theater_id=None, title=None, address=None, latitude=None, longitude=None,
                 description=None,  phone1=None,  phone2=None,  phone3=None):
        self.metro_id = metro_id
        self.yandex_theater_id = yandex_theater_id
        self.title = title
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        self.phone1 = phone1
        self.phone2 = phone2
        self.phone3 = phone3

    def __repr__(self):
        return '<{} Movie_theater>'.format(self.title)


class TimeSlots(Base):
    __tablename__ = "time_slots"
    id = Column(Integer, primary_key=True)
    movie_theaters_id = Column(Integer, ForeignKey('movie_theaters.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    movie_formats_id = Column(Integer, ForeignKey('movie_formats.id'))
    time = Column(DateTime)
    max_price = Column(Integer())
    min_price = Column(Integer())
    __table_args__ = (UniqueConstraint('movie_theaters_id', 'movie_id',
                                       'movie_formats_id', 'time', name='time_slot_uniqueness'),)

    def __init__(self, max_price=None, min_price=None, movie_theaters_id=None, movie_id=None,
                 movie_formats_id=None, time=None):
        self.movie_theaters_id = movie_theaters_id
        self.movie_id = movie_id
        self.movie_formats_id = movie_formats_id
        self.time = time
        self.max_price = max_price
        self.min_price = min_price

    def __repr__(self):
        return '< {} at {} in {} >'.format(self.movie_id, self.time, self.movie_theaters_id)


class Movies(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    yandex_movie_id = Column(String(140))
    title = Column(String(200))
    genre = Column(String(200))
    description = Column(Text)
    duration = Column(Integer, default=0)
    movie_status = Column(Integer, default=0)
    create_date = Column(DateTime)
    start_date = Column(String(120))
    rating = Column(Float, default=0)
    trailer_url = Column(Text)
    time_slots = relationship('TimeSlots', backref='movie')
    __table_args__ = (UniqueConstraint('yandex_movie_id', 'title', name='movie_uniqueness'),)

    def __str__(self):
        return self.title


class MovieFormats(Base):
    __tablename__ = "movie_formats"
    id = Column(Integer, primary_key=True)
    title = Column(String(120))
    time_slots = relationship('TimeSlots', backref='movie_format')

    def __init__(self, title=None):
        self.title = title

    def __repr__(self):
        return '<{}>'.format(self.title)


class PlotKeyword(Base):
    __tablename__ = 'tmdb_plot_keywords'
    id = Column(Integer, primary_key=True)
    keyword = Column(String(500), unique=True)

    def __str__(self):
        return self.keyword


class MoviesKeywords(Base):
    __tablename__ = 'tmdb_plot_keywords_connecction'
    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('tmdb_plot_keywords.id'), index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), index=True)


class BotLog(Base):
    __tablename__ = 'bot_logger'
    id = Column(Integer, primary_key=True)
    log_time = Column(DateTime)
    user_telegram_id = Column(Integer())
    user_telegram_name = Column(String(50))
    msg_in = Column(String(500))
    msg_out = Column(String(500))

    def __init__(self, log_time=None, user_telegram_id=None, user_telegram_name=None,msg_in=None,msg_out=None):
        self.user_telegram_id = user_telegram_id
        self.log_time = log_time
        self.user_telegram_name = user_telegram_name
        self.msg_in = msg_in
        self.msg_out = msg_out


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
