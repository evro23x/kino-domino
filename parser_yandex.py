from math import sqrt
from bs4 import BeautifulSoup
from urllib.request import urlopen
from db_schema import db_session, MetroStations, MovieTheaters, TimeSlots, Movies, MovieFormats
from datetime import datetime, date, time, timedelta
import requests
import json

ITERATIONS = 3


def get_or_create(current_session, model, **kwargs):
    instance = current_session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        current_session.add(instance)
        current_session.commit()
        return instance


def get_json_from_url(url):
    return requests.get(url).json()


def check_metro_in_db():
    metro_list = []
    for metro in get_json_from_url('https://api.hh.ru/metro/1')['lines']:
        # print('Парсим все станции метро на ветке - {}'.format(metro['name']))
        for station in metro['stations']:
            metro_from_db = get_or_create(db_session, MetroStations,
                                          title=station['name'],
                                          latitude=station['lat'],
                                          longitude=station['lng'])
            metro_list.append(metro_from_db)
    return metro_list


def check_cinema_in_db(all_metro):
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

        # print(cinema['id'])
        # print(metro_st_id)
        # print(cinema['coordinates']['latitude'])
        # print(cinema['coordinates']['longitude'])
        # print(cinema['address'])
        # print(phones[0])
        # print(phones[1])
        # print(phones[2])
        # print('++++++++++++++++++++++++++++++++')
        # exit()
        # print('Парсим всю инфу по кт - {}'.format(cinema['title']))
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
        # exit()
    return cinema_list


def get_metro_stations_from_db():
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
    return min(data, key=lambda data: get_distance(latitude, longitude, data['latitude'], data['longitude']))


def get_distance(x1, y1, point_x1, point_y1):
    return sqrt((x1 - point_x1) ** 2 + (y1 - point_y1) ** 2)


def check_movie_in_db():
    # Комент для себя =) чтобы потом вспомнить как это работает.
    # Собираем сначала список новых фильмов(премьерных) + первая страница всех остальных
    # склеиваем два списка и отправляется в цикл по перебору всех страниц списка фильмов
    # далее итоговый список всех фильмов перебираем и складываем в базу
    # TODO дублирующие записи в таблице фильмов из-за изменения рейтинга(при запуске парсера)
    # рейтинг часто меняется и каждый раз при запуске парсера добавляется
    # дублирующая запись в таблицу фильмов, отличие только в рейтинге фильма -> hotfix!

    url_new_movie_list = 'https://afisha.yandex.ru/api/events/actual?limit=12&offset=0&tag=cinema&hasMixed=0&' \
                         'filter=week-premiere&city=moscow'
    new_movie_list = get_json_from_url(url_new_movie_list)
    # print(json.dumps(new_movie_list, sort_keys=True, indent=4, ensure_ascii=False))

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
        # print('Парсим фильм {}'.format(movie['event']['title']))
        get_or_create(db_session, Movies,
                      yandex_movie_id=movie['event']['id'],
                      title=movie['event']['title'],
                      start_date=movie['scheduleInfo']['dateReleased'],
                      rating=str(movie['rank']))
    return movies_id


def get_theater_id_by_yandex_id(yandex_theater_id):
    theater = db_session.query(MovieTheaters).filter_by(yandex_theater_id=yandex_theater_id).first()
    return theater.id


def get_movie_id_by_yandex_id(yandex_movie_id):
    theater = db_session.query(Movies).filter_by(yandex_movie_id=yandex_movie_id).first()
    return theater.id


def check_time_slot_in_db(movies_id):
    counter = 0
    # print('начало начал')
    for yandex_movie_id in movies_id:
        # print('зашел в первый иф')
        while counter < ITERATIONS:
            # print('пришли в вайл')
            session_date = date.today() + timedelta(counter)
            counter += 1
            header = 'https://afisha.yandex.ru/api/events/'
            date_params = '&date=' + str(session_date) + '&city=moscow'
            test_url = header + yandex_movie_id + '/schedule_cinema?limit=10&offset=0' + date_params
            # print(test_url)
            # exit()
            first_query_json = get_json_from_url(test_url)['schedule']
            # print('выполнил запрос')
            # print(json.dumps(first_query_json, sort_keys=True, indent=4, ensure_ascii=False))
            # print(time_slot_list)
            # exit()
            if first_query_json['paging']['total'] == 0:
                # print('проскочил в континуе')
                continue
            for i in range(int(first_query_json['paging']['total'] / 10 + 1)):
                # print('зашел в фор')
                limit_offset = '/schedule_cinema?limit=10&offset=' + str(i * 10)
                url = header + yandex_movie_id + limit_offset + date_params
                # print('собрал второй урик')

                time_slot_list = get_json_from_url(url)['schedule']
                # print('выполнил второй запрос')
                # print(json.dumps(time_slot_list, sort_keys=True, indent=4, ensure_ascii=False))
                # print(time_slot_list)
                # exit()

                for time_slot in time_slot_list['items']:
                    theater_id_from_json = time_slot['place']['id']
                    movie_format_from_json = time_slot['schedule']['format']['name']
                    datetime_from_json = time_slot['schedule']['sessions']['datetime']
                    max_price_from_json = time_slot['schedule']['sessions']['ticket']['price']['max']
                    min_price_from_json = time_slot['schedule']['sessions']['ticket']['price']['min']

                    movie_format = get_or_create(db_session, MovieFormats, title=movie_format_from_json)
                    print(get_theater_id_by_yandex_id(theater_id_from_json))
                    print(get_movie_id_by_yandex_id(yandex_movie_id))
                    print(movie_format.id)
                    print(datetime.strptime(datetime_from_json, "%Y-%m-%dT%H:%M:%S"))
                    print(max_price_from_json)
                    print(min_price_from_json)
                    print('++++++++++++++++++++++++++++++++')
                    print('')

                    # get_or_create(db_session, TimeSlots,
                    #               movie_theaters_id=get_theater_id_by_yandex_id(theater_id_from_json),
                    #               movie_id=get_movie_id_by_yandex_id(yandex_movie_id),
                    #               movie_formats_id=movie_format.id,
                    #               time=datetime.strptime(datetime_from_json, "%Y-%m-%dT%H:%M:%S"),
                    #               max_price=max_price_from_json,
                    #               min_price=min_price_from_json)


def main():
    # pass
    all_metro = check_metro_in_db()
    check_cinema_in_db(all_metro)
    movies_id_list = check_movie_in_db()
    check_time_slot_in_db(movies_id_list)


if __name__ == '__main__':
    main()
