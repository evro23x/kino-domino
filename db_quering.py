import calendar
from datetime import datetime, timedelta
from geopy.distance import vincenty
from db_schema import MovieTheaters, Movies, db_session, TimeSlots, MovieFormats


class UserRequestFail(Exception):
    def __init__(self):
        Exception.__init__(self, "failed to process user request")


class FindTheaterFail(Exception):
    def __init__(self):
        Exception.__init__(self, "failed to find movie theater")


# Узнаем id фильма
def get_current_movie_id(user_input):
    movie = Movies.query.filter(Movies.time_slots.any() , Movies.title.ilike("%{}%".format(user_input))).first()
    if movie:
        return movie.id


def find_closest_theater(user_coordinates, movie_id):
    movie_slots = db_session.query(TimeSlots).filter(TimeSlots.movie_id == movie_id, 
                                                    TimeSlots.time.between(datetime.now(),datetime.now()+timedelta(days=3))).all()
    theaters_coordinates = []
    for slot in movie_slots:
        theaters_coordinates.append((slot.theater.latitude, slot.theater.longitude))
    if theaters_coordinates:
        closest_coordinates = min(theaters_coordinates, key=lambda coordinates: vincenty(coordinates, user_coordinates).km)
        closest_theater_id = MovieTheaters.query.filter(MovieTheaters.latitude == closest_coordinates[0], 
            MovieTheaters.longitude == closest_coordinates[1]).first().id
        return closest_theater_id
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
    first_date = datetime.date(time_table[0].time)
    result += "{}\n".format(movie_name)
    result += "{}({}):\n".format(first_date, calendar.day_name[datetime.weekday(first_date)])
    for time_slot in time_table:
        new_date = datetime.date(time_slot.time)
        if new_date != first_date:
            result += "{}({}):\n".format(new_date, calendar.day_name[datetime.weekday(new_date)])
        starting_time = time_slot.time
        result += "Сеанс в {:%H:%M} формат - {}, цены: {}-{}\n".format(
            datetime.time(starting_time),
            MovieFormats.query.filter(
            MovieFormats.id == time_slot.movie_formats_id).first().title,
        time_slot.min_price/100, time_slot.max_price/100
        )
    return result


def main_search(user_input, user_coordinates):
    try:
        movie_id = get_current_movie_id(user_input)
    except(UserRequestFail):
        return "Прости! я всего лишь бот, я не нашел такого фильма, либо нашел слишком много! Уточни запрос."
    try:
        closest_theater_id = find_closest_theater(user_coordinates, movie_id)
    except(FindTheaterFail):
        return "Прости я всего лишь бот, я не нашел кинотеатров где сейчас идет этот фильм!"
    time_table = get_movie_slots_in_theater_at_period(movie_id, closest_theater_id, 
        datetime.now(),
        datetime.now()+timedelta(days=3))
    return parse_time_table(time_table)


if __name__ == '__main__':
    #pass
    user_coordinates = (55.736796, 37.586822)
    #movie_id = 1
    #print(find_closest_theater(user_coordinates, movie_id))
    user_input = "логан"
    print(main_search(user_input, user_coordinates))
    #print(get_current_movie_id(user_input))
    #movie_slots = db_session.query(TimeSlots).filter(TimeSlots.movie_id == movie_id).all()
    #print(movie_slots[0].theater.latitude)
