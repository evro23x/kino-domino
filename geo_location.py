from geopy.geocoders import Yandex
from db_schema import db_session, MovieTheaters

geolocator = Yandex(timeout=99)


def convert_adress_to_coordinates(adress):
    location = geolocator.geocode(adress)
    if location == None:
        return (0.0, 0.0)
    else:
        return location.latitude, location.longitude


# Делаем проход по строкам в БД, конвертируем адресс в координаты,
# записываем в соотвествующие колонки "широта" и "долгота"
def adding_movie_theaters_coordinates_to_DB():
    adresses = db_session.query(MovieTheaters.address).all()
    list_of_coordinates = []
    for adress in adresses:
        list_of_coordinates.append(convert_adress_to_coordinates(adress))
    for coordinates, theater in zip(list_of_coordinates, db_session.query(MovieTheaters)):
        theater.latitude = coordinates[0]
        theater.longitude = coordinates[1]
    db_session.commit()

def second_pass_adding_theaters_coordinates_to_DB():
    list_of_theaters = MovieTheaters.query.filter(MovieTheaters.latitude == 0.0).all()
    for theater in list_of_theaters:
        theater.latitude, theater.longitude = convert_adress_to_coordinates(theater.address)
    db_session.commit()

if __name__ == '__main__':
    #second_pass_adding_theaters_coordinates_to_DB()
    #adding_movie_theaters_coordinates_to_DB()
    #adress = "Ярцевская, 19, МФК «Кунцево-плаза»"
    #print(convert_adress_to_coordinates(adress))