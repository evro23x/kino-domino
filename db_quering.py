from geopy.distance import vincenty
from db import MovieTheaters, Movies, db_session


# Узнаем id фильма
def get_movie_id(user_input):
    return Movies.query.filter(Movies.title == user_input).first().id

# проверяем идет ли указанный пользователем фильм в кинотеатре
def is_on_screen(movie_theater_id, user_movie):
    time_table = get_time_table_of_theater_by_id(movie_theater_id)
    for time_slot in time_table:
        if time_slot.movie_id == Movies.query.filter(Movies.title == user_movie).first().id:
            return True
        else:
            return False


# На основе геопозиции пользователя, выводим id
# ближайшего кинотеатра где идет указанный пользователем фильм
def find_closest_theater(user_coordinates, user_movie):
    closest_theater = [100,"Name"]
    for theater in db_session.query(MovieTheaters):
        coordinates = theater.latitude, theater.longitude
        movie_theater_id = theater.id
        distance = vincenty(coordinates, user_coordinates).km
        if distance < closest_theater[0] and is_on_screen(movie_theater_id, user_movie):
            closest_theater[0] = distance
            closest_theater[1] = theater.id
    return closest_theater[1]


# выдаем все расписание кинотеатра в виде листа экземпляров класса TimeSlot
def get_time_table_of_theater_by_id(movie_theater_id):
    return MovieTheaters.query.filter(MovieTheaters.id == movie_theater_id).first().time_slots


# выводим строку человеко-читаемого текста все сеансы фильма, указанного юзером
def parse_time_table(time_table, movie_id):
    movie_theater_id = time_table[0].movie_theaters_id
    movie_theater_name = MovieTheaters.query.filter(MovieTheaters.id == movie_theater_id).first().title
    result = "Расписание кинотеатра {} :\n".format(movie_theater_name)
    for time_slot in time_table:
        if time_slot.movie_id == movie_id:
            starting_time = time_slot.time
            cost = time_slot.cost
            movie_name = Movies.query.filter(Movies.id == movie_id).first().title
            result += "{} в {}, цена билета {}\n".format(movie_name, starting_time, cost)
    return result
        

if __name__ == '__main__':
    #print(parse_time_table(get_time_table_of_theater_by_id(1)))
    #print(is_on_screen(1, "Хранители справедливости"))
    #print(is_on_screen(2, "Хранители справедливости"))
    #print(find_closest_theater((55.7796266,37.5992518),"Хранители справедливости"))
    print(parse_time_table(get_time_table_of_theater_by_id(1), 2))
    