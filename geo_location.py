from geopy.geocoders import Yandex
from db_schema import db_session, MovieTheaters


GEO_LOCATOR = Yandex(timeout=99)


def convert_adress_to_coordinates(adress):
    location = geolocator.geocode(adress)
    if location == None:
        return (0.0, 0.0)
    else:
        return location.latitude, location.longitude


# Делаем проход по строкам в БД, конвертируем адресс в координаты,
# записываем в соотвествующие колонки "широта" и "долгота"
def add_movie_theaters_coordinates_to_DB():
    theaters = db_session.query(MovieTheaters)
    list_of_coordinates = []
    for theater in theaters:
        theater.latitude, theater.longitude = convert_adress_to_coordinates(theater.address)
    db_session.commit()


def second_pass_adding_theaters_coordinates_to_DB():
    list_of_theaters = MovieTheaters.query.filter(MovieTheaters.latitude == 0.0).all()
    for theater in list_of_theaters:
        theater.latitude, theater.longitude = convert_adress_to_coordinates(theater.address)
    db_session.commit()


if __name__ == '__main__':
    adding_movie_theaters_coordinates_to_DB()
    second_pass_adding_theaters_coordinates_to_DB()
