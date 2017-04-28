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
def get_current_movie_id(movies_title):
    movie = Movies.query.filter(Movies.time_slots.any(), Movies.title.ilike("%{}%".format(movies_title))). \
        order_by(Movies.id.desc()).first()
    if movie:
        return movie.id


def get_theater_by_name(theaters_title):
    theater = MovieTheaters.query.filter(MovieTheaters.title.ilike("%{}%".format(theaters_title))).first()
    if theater:
        return theater


def get_theater_by_id(theater_id):
    theater = MovieTheaters.query.filter(MovieTheaters.id == theater_id).first()
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


# первый вариант
# два запроса
# первый вытаскивает уникальные значения названий фильма и формата по кт на дату
# второй вытаскивает все сеансы заданного фильма/формата/кт/на дату

# второй вариант
# одним запросом получаем всю информацию по кт на дату
# структурируем на уровне языка


def get_time_table_by_theater_id_at_period(theater_id, date_from, date_to):
    print(theater_id, date_from, date_to)
    print(db_session.query(TimeSlots, Movies, MovieFormats, MovieTheaters).filter(TimeSlots.movie_id == Movies.id). \
          filter(TimeSlots.movie_theaters_id == MovieTheaters.id).filter(TimeSlots.movie_formats_id == MovieFormats.id). \
          filter(TimeSlots.movie_theaters_id == theater_id, TimeSlots.time.between(date_from, date_to)). \
          order_by(TimeSlots.movie_id, TimeSlots.movie_formats_id, TimeSlots.time))
    return db_session.query(TimeSlots, Movies, MovieFormats, MovieTheaters).filter(TimeSlots.movie_id == Movies.id). \
        filter(TimeSlots.movie_theaters_id == MovieTheaters.id).filter(TimeSlots.movie_formats_id == MovieFormats.id). \
        filter(TimeSlots.movie_theaters_id == theater_id, TimeSlots.time.between(date_from, date_to)). \
        order_by(TimeSlots.movie_id, TimeSlots.movie_formats_id, TimeSlots.time).all()


def prepare_theater_timetable(theater_id, date_from, date_to):
    print(4)
    time_table = get_time_table_by_theater_id_at_period(theater_id, date_from, date_to)
    print(5)
    if time_table:
        print(6)
        result = "Расписание кинотеатра - {}\nДата - {:%d-%m-%Y}({}):\n".format(time_table[0][3].title, date_from,
                                                                                DAYS[datetime.weekday(date_from)])
        tmp_dict = dict(movie='', movie_format='')
        for time_slot in time_table:
            if time_slot[1].title not in tmp_dict.values():
                tmp_dict.update(movie=time_slot[1].title, movie_format=time_slot[2])
                result += "\n{}\nФормат - {}\n".format(time_slot[1].title, str(time_slot[2])[1:-1])

            if time_slot[1].title in tmp_dict.values() and time_slot[2] not in tmp_dict.values():
                tmp_dict.update(movie=time_slot[1].title, movie_format=time_slot[2])
                result += "Формат - {}\n".format(str(time_slot[2])[1:-1])

            min_price = time_slot[0].min_price
            max_price = time_slot[0].max_price

            result += "Сеанс в {:%H:%M}".format(datetime.time(time_slot[0].time))
            if 0 < min_price != max_price > 0:
                result += ", цена: {}-{}".format(int(min_price / 100), int(max_price / 100))
            elif min_price == 0 and max_price > 0:
                result += ", цена: {}".format(int(max_price / 100))
            elif min_price > 0 and max_price == 0:
                result += ", цена: {}".format(int(min_price / 100))
            elif 0 < min_price == max_price > 0:
                result += ", цена: {}".format(int(min_price / 100))
            result += "\n"
    else:
        result = "Расписание кинотеатра {} на дату {:%d-%m-%Y} не найдено\n".format(
            get_theater_by_id(theater_id).title, date_from)
    return result


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
            result += "\n{:%d-%m-%Y}({}):\n".format(query_date, DAYS[datetime.weekday(query_date)])
            unique_movie_format_list = set()
            for time_slot in time_table:
                curr_format = str(movie_format_list[time_slot.movie_formats_id - 1])[1:-1]
                if curr_format not in unique_movie_format_list:
                    result += "Формат - {}\n".format(curr_format)
                unique_movie_format_list.add(curr_format)
                result += "Сеанс в {:%H:%M}".format(datetime.time(time_slot.time))
                if 0 < time_slot.min_price != time_slot.max_price > 0:
                    result += ", цена: {}-{}".format(int(time_slot.min_price / 100), int(time_slot.max_price / 100))
                elif time_slot.min_price == 0 and time_slot.max_price > 0:
                    result += ", цена: {}".format(int(time_slot.max_price / 100))
                elif time_slot.min_price > 0 and time_slot.max_price == 0:
                    result += ", цена: {}".format(int(time_slot.min_price / 100))
                elif 0 < time_slot.min_price == time_slot.max_price > 0:
                    result += ", цена: {}".format(int(time_slot.min_price / 100))
                result += "\n"
    return result


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
    # print(get_time_table_by_theater_id_at_period(21, datetime.now().date(), date.today() + timedelta(1)))
    # print(prepare_theater_timetable(21, datetime.now(), date.today() + timedelta(1)))
    print(prepare_theater_timetable(21, date.today() + timedelta(1), date.today() + timedelta(2)))
    # print(prepare_theater_timetable(21, date.today() + timedelta(2), date.today() + timedelta(3)))
