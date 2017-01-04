from geopy.geocoders import Yandex
from geopy.distance import vincenty
from db import db_session, MovieTheaters

geolocator = Yandex()


def convert_adress_to_coordinates(adress):
    location = geolocator.geocode(adress)
    return location.latitude, location.longitude

# На основе геопозиции пользователя, выводим id
# ближайшего кинотеатра
def find_closest_theater(user_coordinates):
    closest_theater = [100,"Name"]
    for theater in db_session.query(MovieTheaters):
        coordinates = theater.latitude, theater.longitude
        distance = vincenty(coordinates, user_coordinates).km
        if distance < closest_theater[0]:
            closest_theater[0] = distance
            closest_theater[1] = theater.id
    return closest_theater[1]


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