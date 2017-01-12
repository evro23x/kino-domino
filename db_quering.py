from geopy.distance import vincenty
from db import MovieTheaters, Movies, db_session


# Узнаем id фильма
def get_movie_id(user_input):
    output_query = Movies.query.filter(Movies.title.like("%"+user_input[1:]+"%")).all()
    if len(output_query) == 1:
        return output_query[0].id


# проверяем идет ли указанный пользователем фильм в кинотеатре
def is_on_screen(movie_theater_id, movie_id):
    time_table = get_time_table_of_theater_by_id(movie_theater_id)
    for time_slot in time_table:
        if time_slot.movie_id == movie_id:
            return True
        else:
            return False


# На основе геопозиции пользователя, выводим id
# ближайшего кинотеатра где идет указанный пользователем фильм
def find_closest_theater(user_coordinates, movie_id):
    closest_theater = [100,"Name"]
    for theater in db_session.query(MovieTheaters):
        coordinates = theater.latitude, theater.longitude
        movie_theater_id = theater.id
        distance = vincenty(coordinates, user_coordinates).km
        if distance < closest_theater[0] and is_on_screen(movie_theater_id, movie_id):
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
        

def main_search(user_input, user_coordinates):
    movie_id = get_movie_id(user_input)
    closest_theater_id = find_closest_theater(user_coordinates, movie_id)
    time_table = get_time_table_of_theater_by_id(closest_theater_id)
    return parse_time_table(time_table, movie_id)


if __name__ == '__main__':
    #print(main_search("хранители", (55.7796266,37.5992518)))
    