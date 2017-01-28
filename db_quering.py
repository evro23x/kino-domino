from datetime import datetime, timedelta
from geopy.distance import vincenty
from db_schema import MovieTheaters, Movies, db_session, TimeSlots


class UserRequestFail(Exception):
    def __init__(self):
        Exception.__init__(self, "failed to process user request")


class FindTheaterFail(Exception):
    def __init__(self):
        Exception.__init__(self, "failed to find movie theater")


# Узнаем id фильма
def get_movie_id(user_input):
    movie = Movies.query.filter(Movies.title.ilike("%{}%".format(user_input[1:-1]))).first()
    if movie:
        return movie.id


# надо переписать с учетом дат
def is_on_screen(movie_theater_id, movie_id):
    time_table = MovieTheaters.query.filter(MovieTheaters.id == movie_theater_id).first().time_slots
    is_movie_in_table = False
    for time_slot in time_table:
        if time_slot.movie_id == movie_id:
            is_movie_in_table = True
    return is_movie_in_table


def find_closest_theater2(user_coordinates, movie_id):
    theaters_coordinates = db_session.query(MovieTheaters.latitude, MovieTheaters.longitude).all()
    is_theater_found = False
    while not is_theater_found:
        if theaters_coordinates:
            closest_coordinates = min(theaters_coordinates, key=lambda coordinates: vincenty(coordinates, user_coordinates).km)
            closest_theater_id = MovieTheaters.query.filter(MovieTheaters.latitude == closest_coordinates[0], 
                MovieTheaters.longitude == closest_coordinates[1]).first().id
            if is_on_screen(closest_theater_id, movie_id):
                is_theater_found = True
                return closest_theater_id
            else:
                theaters_coordinates.remove(closest_coordinates)
        else:
            raise FindTheaterFail()


def find_closest_theater(user_coordinates, movie_id):
    """
        На основе геопозиции пользователя, выводим id
        ближайшего кинотеатра где идет указанный пользователем фильм
    """
    closest_theater = [100,""]
    for theater in db_session.query(MovieTheaters):
        coordinates = theater.latitude, theater.longitude
        movie_theater_id = theater.id
        distance = vincenty(coordinates, user_coordinates).km
        if distance < closest_theater[0] and is_on_screen(movie_theater_id, movie_id):
            closest_theater[0] = distance
            closest_theater[1] = theater.id
    if closest_theater[1]:
        return closest_theater[1]
    else:
        raise FindTheaterFail()


def get_movie_slots_in_theater_at_period(movie_id, theater_id, date_from, date_to):
    return TimeSlots.query.filter(
        TimeSlots.movie_id == movie_id,
        TimeSlots.movie_theaters_id == theater_id,
        TimeSlots.time.between(date_from, date_to)
    ).order_by('time').all()


def parse_time_table(time_table):
    movie_theater_id = time_table[0].movie_theaters_id
    movie_theater_name = MovieTheaters.query.filter(MovieTheaters.id == movie_theater_id).first().title
    movie_name = Movies.query.filter(Movies.id == time_table[0].movie_id).first().title
    result = "Расписание кинотеатра {} :\n".format(movie_theater_name)
    for time_slot in time_table:
        starting_time = time_slot.time
        result += "{} в {}\n".format(movie_name, starting_time)
    return result


# итоговая функция поменять datetime(....) на datetime.now() база старая поэтому дату сейчас хардкодим
def main_search(user_input, user_coordinates):
    try:
        movie_id = get_movie_id(user_input)
    except(UserRequestFail):
        return "Прости! я всего лишь бот, я не нашел такого фильма, либо нашел слишком много! Уточни запрос."
    try:
        closest_theater_id = find_closest_theater(user_coordinates, movie_id)
    except(FindTheaterFail):
        return "Прости я всего лишь бот, я не нашел кинотеатров где сейчас идет этот фильм!"
    time_table = get_movie_slots_in_theater_at_period(movie_id, closest_theater_id, 
        datetime(year=2017, month=1, day=19, hour=0),
        datetime.now()+timedelta(days=3))
    return parse_time_table(time_table)


if __name__ == '__main__':
    user_coordinates = (55.7846095,37.5880045)
    #print(find_closest_theater2(user_coordinates, movie_id))
    #print(find_closest_theater(user_coordinates, movie_id))
    print(main_search("пассажиры", user_coordinates))