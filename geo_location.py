from geopy.geocoders import Yandex
from db_schema import db_session, MovieTheaters

geolocator = Yandex()


def convert_adress_to_coordinates(adress):
    location = geolocator.geocode(adress)
    return location.latitude, location.longitude


# Делаем проход по строкам в БД, конвертируем адресс в координаты,
# записываем в соотвествующие колонки "широта" и "долгота"
def adding_movie_theaters_coordinates_to_DB():
    adresses = db_session.query(MovieTheaters.adress).all()
    list_of_coordinates = []
    for adress in adresses:
        list_of_coordinates.append(convert_adress_to_coordinates(adress))
    for coordinates, theater in zip(list_of_coordinates, db_session.query(MovieTheaters)):
        theater.latitude = coordinates[0]
        theater.longitude = coordinates[1]
    db_session.commit()


if __name__ == '__main__':
    adding_movie_theaters_coordinates_to_DB()