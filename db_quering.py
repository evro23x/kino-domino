from db import MovieTheaters, Movies


# выдаем все расписание кинотеатра в виде листа экземпляров класса TimeSlot
def get_time_table_of_theater_by_id(movie_theater_id):
    return MovieTheaters.query.filter(MovieTheaters.id == movie_theater_id).first().time_slots


# выводим строку человеко-читаемого текста
def parse_time_table(time_table):
    movie_theater_id = time_table[0].movie_theaters_id
    movie_theater_name = MovieTheaters.query.filter(MovieTheaters.id == movie_theater_id).first().title
    result = "Расписание кинотеатра {} :\n".format(movie_theater_name)
    for time_slot in time_table:
        movie_name = Movies.query.filter(Movies.id == time_slot.movie_id).first().title
        starting_time = time_slot.time
        result += "{} в {}\n".format(movie_name, starting_time)
    return result
        

if __name__ == '__main__':
    print(parse_time_table(get_time_table_of_theater_by_id(1)))