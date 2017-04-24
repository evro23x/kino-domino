import calendar
from datetime import datetime, date, timedelta
from geopy.distance import vincenty
from db_schema import MovieTheaters, Movies, db_session, TimeSlots, MovieFormats

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

# print(date.today())
# print(date.today() + timedelta(1))
# print(datetime.now() + timedelta(1))
# exit(0)

class UserRequestFail(Exception):
    def __init__(self):
        Exception.__init__(self, "failed to process user request")


class FindTheaterFail(Exception):
    def __init__(self):
        Exception.__init__(self, "failed to find movie theater")


# Узнаем id фильма
def get_current_movie_id(user_input):
    movie = Movies.query.filter(Movies.time_slots.any(), Movies.title.ilike("%{}%".format(user_input))).first()
    if movie:
        return movie.id


def get_theater_by_name(user_input):
    theater = MovieTheaters.query.filter(MovieTheaters.title.ilike("%{}%".format(user_input))).first()
    if theater:
        return theater


def find_closest_theater(user_coordinates, movie_id):
    movie_slots = db_session.query(TimeSlots).filter(TimeSlots.movie_id == movie_id,
                                                     TimeSlots.time.between(datetime.now(),
                                                                            datetime.now() + timedelta(days=3))).all()
    theaters_coordinates = []
    for slot in movie_slots:
        theaters_coordinates.append((slot.theater.latitude, slot.theater.longitude))
    if theaters_coordinates:
        closest_coordinates = min(theaters_coordinates,
                                  key=lambda coordinates: vincenty(coordinates, user_coordinates).km)
        closest_theater_id = MovieTheaters.query.filter(MovieTheaters.latitude == closest_coordinates[0],
                                                        MovieTheaters.longitude == closest_coordinates[1]).first().id
        return closest_theater_id
    else:
        raise FindTheaterFail()


def get_repertoire_by_theater_id_at_period(theater_id, date_from, date_to):
    return TimeSlots.query.filter(
        TimeSlots.movie_theaters_id == theater_id,
        TimeSlots.time.between(date_from, date_to)
    ).order_by('time').all()


def get_movie_slots_in_theater_at_period(movie_id, theater_id, date_from, date_to):
    return TimeSlots.query.filter(
        TimeSlots.movie_id == movie_id,
        TimeSlots.movie_theaters_id == theater_id,
        TimeSlots.time.between(date_from, date_to)
    ).order_by('time').all()


def get_movie_slots_in_theater_at_day(movie_id, theater_id, query_date):
    date_to = query_date + timedelta(1)
    current_time = datetime.now()
    return TimeSlots.query.filter(
        TimeSlots.movie_id == movie_id,
        TimeSlots.movie_theaters_id == theater_id,
        TimeSlots.time > current_time,
        TimeSlots.time.between(query_date, date_to)
    ).order_by('movie_formats_id', 'time').all()


def prepare_time_table(movie_id, closest_theater_id):
    movie_format_list = MovieFormats.query.all()
    movie_theater_name = MovieTheaters.query.filter(MovieTheaters.id == closest_theater_id).first().title
    movie_name = Movies.query.filter(Movies.id == movie_id).first().title
    result = "Расписание кинотеатра {} :\n{}\n".format(movie_theater_name, movie_name)

    for counter in range(3):
        query_date = date.today() + timedelta(counter)
        time_table = get_movie_slots_in_theater_at_day(movie_id, closest_theater_id, query_date)
        if time_table:
            result += "\n{}({}):\n".format(query_date, DAYS[datetime.weekday(query_date)])
            unique_movie_format_list = set()
            for time_slot in time_table:
                curr_format = str(movie_format_list[time_slot.movie_formats_id-1])[1:-1]
                if curr_format not in unique_movie_format_list:
                    result += "Формат - {}\n".format(curr_format)
                unique_movie_format_list.add(curr_format)
                result += "Сеанс в {:%H:%M}".format(datetime.time(time_slot.time))
                if 0 < time_slot.min_price != time_slot.max_price > 0:
                    result += ", цена: {}-{}".format(int(time_slot.min_price/100), int(time_slot.max_price/100))
                elif time_slot.min_price == 0 and time_slot.max_price > 0:
                    result += ", цена: {}".format(int(time_slot.max_price/100))
                elif time_slot.min_price > 0 and time_slot.max_price == 0:
                    result += ", цена: {}".format(int(time_slot.min_price / 100))
                elif 0 < time_slot.min_price == time_slot.max_price > 0:
                    result += ", цена: {}".format(int(time_slot.min_price/100))
                result += "\n"
    return result
    #
    # movie_theater_id = time_table[0].movie_theaters_id
    # movie_theater_name = MovieTheaters.query.filter(MovieTheaters.id == movie_theater_id).first().title
    # movie_name = Movies.query.filter(Movies.id == time_table[0].movie_id).first().title
    # result = "Расписание кинотеатра {} :\n{}\n".format(movie_theater_name, movie_name)
    # first_date = datetime.date(time_table[0].time)
    # result += "{}({}):\n".format(first_date, calendar.day_name[datetime.weekday(first_date)])
    # for time_slot in time_table:
    #     new_date = datetime.date(time_slot.time)
    #     if new_date != first_date:
    #         result += "{}({}):\n".format(new_date, calendar.day_name[datetime.weekday(new_date)])
    #     starting_time = time_slot.time
    #     result += "Сеанс в {:%H:%M} формат - {}, цены: {}-{}\n".format(
    #         datetime.time(starting_time),
    #         MovieFormats.query.filter(
    #             MovieFormats.id == time_slot.movie_formats_id).first().title,
    #         time_slot.min_price / 100, time_slot.max_price / 100
    #     )
    # return result


def main_search(user_input, user_coordinates):
    try:
        movie_id = get_current_movie_id(user_input)
    except(UserRequestFail):
        return "Прости! Я всего лишь бот, я не нашел такого фильма, либо нашел слишком много! Уточни запрос."
    try:
        closest_theater_id = find_closest_theater(user_coordinates, movie_id)
    except(FindTheaterFail):
        return "Прости! Я всего лишь бот, я не нашел кинотеатров где сейчас идет этот фильм!"
    return prepare_time_table(movie_id, closest_theater_id)


if __name__ == '__main__':
    pass
    # print(TimeSlots.query.filter(TimeSlots.movie_theaters_id ==
    # theater_id, TimeSlots.time.between(date_from, date_to)).order_by('time').all())
    a = TimeSlots.query.filter(TimeSlots.movie_theaters_id == 21, TimeSlots.time.between(date.today(), date.today() + timedelta(1))).order_by('time').all()
    for a1 in a:
        print(a1.movie_id, a1.time)
    # print(TimeSlots.query.filter(TimeSlots.movie_theaters_id == 21, TimeSlots.time.between(date.today(), date.today() + timedelta(1))).order_by('time').all())
    # get_repertoire_by_theater_id_at_period(21, datetime.now(), date.today() + timedelta(1))
    # get_theater_by_name("asd")
    # user_input = "логан"
    # print(main_search(user_input, user_coordinates))
    # print(get_current_movie_id(user_input))
    # movie_slots = db_session.query(TimeSlots).filter(TimeSlots.movie_id == movie_id).all()
    # print(movie_slots[0].theater.latitude)
