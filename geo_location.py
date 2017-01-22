from geopy.geocoders import Yandex
from db_schema import db_session, MovieTheaters
from geo_coder import ParametrisibleYandexGeoCoder


GEO_LOCATOR = ParametrisibleYandexGeoCoder(timeout=99)


def convert_adress_to_coordinates(adress):
    location = GEO_LOCATOR.geocode(adress, extra_params="ll=37.618920,55.756994&spn=1,1")
    if location == None:
        return (0.0, 0.0)
    else:
        return location.latitude, location.longitude


def add_movie_theaters_coordinates_to_DB():
    list_of_theaters = MovieTheaters.query.filter(MovieTheaters.latitude == 0.0 or MovieTheaters.longitude == 0.0).all()
    # theaters = db_session.query(MovieTheaters)
    list_of_coordinates = []
    for theater in list_of_theaters:
        theater.latitude, theater.longitude = convert_adress_to_coordinates(theater.address)
    db_session.commit()


if __name__ == '__main__':
     add_movie_theaters_coordinates_to_DB()