from math import sqrt
from bs4 import BeautifulSoup
from db_schema import db_session, MetroStations, MovieTheaters, TimeSlots, Movies, MovieFormats
from datetime import datetime, date, time, timedelta
import requests
import json

ITERATIONS = 3


def get_or_create(current_session, model, **kwargs):
    """
    Получить либо создать

    Функция получения данных из базы по передаваемым параметрам.
    Создает новую запись в базе если запрашиваемый отбъект отсуствует.
    """
    instance = current_session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        current_session.add(instance)
        current_session.commit()
        return instance


def get_json_from_url(url):
    """
    Получить json по ссылке

    Обертка над получением данных в формате json по передаваемой ссылке
    """
    return requests.get(url).json()


def check_metro_in_db():
    """
    Актуализация перечня станций метро

    Разбираем станции метро полученные от api hh и складываем в базу.
    Информация о существующих станциях метро неизменна.
    Количество станций может добавляться использую функцию get_or_create.
    """
    metro_list = []
    for metro in get_json_from_url('https://api.hh.ru/metro/1')['lines']:
        print('Парсим все станции метро на ветке - {}'.format(metro['name']))
        for station in metro['stations']:
            metro_from_db = get_or_create(db_session, MetroStations,
                                          title=station['name'],
                                          latitude=station['lat'],
                                          longitude=station['lng'])
            metro_list.append(metro_from_db)
    return metro_list


def check_cinema_in_db(all_metro):
    """
    Актуализация перечня кинотеатров

    Разбираем список кинотеатров по Москве от afisha.yandex.ru .
    Расчитываем ближаейшую станцию метро если она не указана в api и записываем данные к нам в базу
    """
    # TODO: Требуется доработать таким образом чтобы функция вызывалась при парсинге сеансов, так как там более
    # удобная структура и оптимизация в количестве запросов, так как сюда уже будет передаваться list и не потребуется
    # повторно вызывать get_json_from_url()
    cinema_list = []
    url_cinema_list = 'https://afisha.yandex.ru/api/events/cinema/places?limit=200&offset=0&city=moscow'
    for cinema in get_json_from_url(url_cinema_list)['items']:

        phones = ['', '', '']
        if cinema['phones'] and len(cinema['phones']) != 0:
            for i in range(len(cinema['phones'][0]['numbers'])):
                phones[i] = cinema['phones'][0]['numbers'][i]

        latitude = float(cinema['coordinates']['latitude'])
        longitude = float(cinema['coordinates']['longitude'])

        if len(cinema['metro']) == 0:
            metro_station = get_closest_station(get_metro_stations_from_db(), latitude, longitude)
            metro_st_id = metro_station['id']
        else:
            for metro in all_metro:
                if metro.title == cinema['metro'][0]['name']:
                    metro_st_id = metro.id
        print('Парсим всю инфу по кт - {}'.format(cinema['title']))
        cinema_list.append(get_or_create(db_session, MovieTheaters,
                                         metro_id=metro_st_id,
                                         yandex_theater_id=cinema['id'],
                                         title=cinema['title'],
                                         latitude=cinema['coordinates']['latitude'],
                                         longitude=cinema['coordinates']['longitude'],
                                         address=cinema['address'],
                                         description="",
                                         phone1=phones[0],
                                         phone2=phones[1],
                                         phone3=phones[2]))
    return cinema_list


def get_metro_stations_from_db():
    """
    Получение всех станций метро из базы.

    """
    metro_list = []
    for u in db_session.query(MetroStations).all():
        result = {
            'id': u.__dict__['id'],
            'title': u.__dict__['title'],
            'latitude': u.__dict__['latitude'],
            'longitude': u.__dict__['longitude'],
        }
        metro_list.append(result)
    return metro_list


def get_closest_station(data, latitude, longitude):
    """
    Поиск ближайшей станции метро.
    """
    return min(data, key=lambda data: get_distance(latitude, longitude, data['latitude'], data['longitude']))


def get_distance(x1, y1, point_x1, point_y1):
    """
    Расчет расстояния между двумя точками.
    """
    return sqrt((x1 - point_x1) ** 2 + (y1 - point_y1) ** 2)


def check_movie_in_db():
    """
    Актуализация перечня фильмов.

    Собираем сначала список новых фильмов(премьерных) + первая страница всех остальных
    склеиваем два списка и отправляется в цикл по перебору всех страниц списка фильмов
    далее итоговый список всех фильмов перебираем и складываем в базу
    """

    url_new_movie_list = 'https://afisha.yandex.ru/api/events/actual?limit=12&offset=0&tag=cinema&hasMixed=0&' \
                         'filter=week-premiere&city=moscow'
    new_movie_list = get_json_from_url(url_new_movie_list)

    url_movie_list = 'https://afisha.yandex.ru/api/events/actual?' \
                     'limit=12&offset=0&tag=cinema&hasMixed=0&date=' + str(date.today()) + '&period=1&city=moscow'
    first_query_json = get_json_from_url(url_movie_list)

    movie_list = new_movie_list['data'] + first_query_json['data']
    movies_id = []
    for i in range(int(first_query_json['paging']['total'] / 12 + 1)):
        url_movie_list = 'https://afisha.yandex.ru/api/events/actual?' \
                         'limit=12&offset=' + str(i * 12) + '&tag=cinema&hasMixed=0' \
                                                            '&date=' + str(date.today()) + '&period=1&city=moscow'

        movie_list = movie_list + get_json_from_url(url_movie_list)['data']
    for movie in movie_list:
        movies_id.append(movie['event']['id'])
        print('Парсим фильм {}'.format(movie['event']['title']))
        get_or_create(db_session, Movies,
                      yandex_movie_id=movie['event']['id'],
                      title=movie['event']['title'],
                      start_date=movie['scheduleInfo']['dateReleased'])
    return movies_id


def get_theater_by_yandex_id(yandex_theater_id):
    """
    Получение инфо о кинотеатре по id кт с афиши яндекса.
    """
    theater = db_session.query(MovieTheaters).filter_by(yandex_theater_id=yandex_theater_id).first()
    return theater if theater else None


def get_movie_by_yandex_id(yandex_movie_id):
    """
    Получение инфо о фильме по id фильма с афиши яндекса.
    """
    movie = db_session.query(Movies).filter_by(yandex_movie_id=yandex_movie_id).first()
    return movie if movie else None


def check_time_slot_in_db(movies_id):
    """
    Актуализация сеансов.

    Получаем по id фильма его id на сайте афиши яндекса и формируем ссылку.
    Достаем рассписание сеансов с постраничной навигацией(перебираем в цикле) и складывам в базу.
    """
    for yandex_movie_id in list(set(movies_id)):
        movie = get_movie_by_yandex_id(yandex_movie_id)
        print('Собираем расписание по фильму - {}'.format(movie.title))
        for counter in range(ITERATIONS):
            session_date = date.today() + timedelta(counter)
            print('На дату - {}'.format(session_date))

            header = 'https://afisha.yandex.ru/api/events/'
            date_params = '&date=' + str(session_date) + '&city=moscow'
            first_query_url = header + yandex_movie_id + '/schedule_cinema?limit=10&offset=0' + date_params

            first_query_result = get_json_from_url(first_query_url)
            paging_count = first_query_result['schedule']['paging']['total']

            # условие на случай если у фильма будет 0 сеансов за день(часто бывает у премьер)
            if paging_count == 0:
                continue
            time_slot_list = []
            for i in range(int(paging_count / 10 + 1)):
                limit_offset = '/schedule_cinema?limit=10&offset=' + str(i * 10)
                paging_time_slot_url = header + yandex_movie_id + limit_offset + date_params
                paging_time_slot_result = get_json_from_url(paging_time_slot_url)
                for raw in paging_time_slot_result['schedule']['items']:
                    time_slot_list.append(raw)
            for time_slot in time_slot_list:
                theater_id_from_json = time_slot['place']['id']
                # print(json.dumps(time_slot, sort_keys=True, indent=4, ensure_ascii=False))
                theater = get_theater_by_yandex_id(theater_id_from_json)

                # условие на случай если кинотеатра не будет в перечне кт(такое редко, но бывает)
                if theater is None:
                    continue
                for movie_formats_separated in time_slot['schedule']:
                    movie_format_from_json = movie_formats_separated['format']['name']
                    movie_format = get_or_create(db_session, MovieFormats, title=movie_format_from_json)
                    for session in movie_formats_separated['sessions']:
                        datetime_from_json = session['datetime']
                        ticket = session['ticket']
                        if ticket is None or ticket['price'] is None:
                            max_price_from_json = 0
                            min_price_from_json = 0
                        else:
                            max_price_from_json = ticket['price']['max']
                            min_price_from_json = ticket['price']['min']

                        get_or_create(db_session, TimeSlots,
                                      movie_theaters_id=theater.id,
                                      movie_id=movie.id,
                                      movie_formats_id=movie_format.id,
                                      time=datetime.strptime(datetime_from_json, "%Y-%m-%dT%H:%M:%S"),
                                      max_price=max_price_from_json,
                                      min_price=min_price_from_json)


def main():
    all_metro = check_metro_in_db()
    check_cinema_in_db(all_metro)
    movies_id_list = check_movie_in_db()
    check_time_slot_in_db(movies_id_list)


if __name__ == '__main__':
    main()
