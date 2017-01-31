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
    for metro in get_json_from_url('https://api.hh.ru/metro/1')['lines']:
        print('Парсим все станции метро на ветке - {}'.format(metro['name']))
        for station in metro['stations']:
            get_or_create(db_session, MetroStations,
                          title=station['name'],
                          latitude=station['lat'],
                          longitude=station['lng'])


def check_cinema_in_db():
    url_cinema_list = 'https://afisha.yandex.ru/api/events/cinema/places?limit=200&offset=0&city=moscow'
    for cinema in get_json_from_url(url_cinema_list)['items']:

        phones = ['', '', '']
        if cinema['phones'] and len(cinema['phones']) != 0:
            for i in range(len(cinema['phones'][0]['numbers'])):
                phones[i] = cinema['phones'][0]['numbers'][i]

        if cinema['metro']:
            metro_stations = MetroStations.query.filter(
                MetroStations.title.ilike("%{}%".format(cinema['metro'][0]['name']))).first()

        if len(cinema['metro']) > 0 and metro_stations is not None:
            metro_st_id = metro_stations.id
        else:
            closest_metro_station = get_closest_metro_station(get_metro_stations_from_db(),
                                                              float(cinema['coordinates']['latitude']),
                                                              float(cinema['coordinates']['longitude']))
            metro_st_id = closest_metro_station['id']

        # print(cinema['id'])
        # print(metro_st_id)
        # print(cinema['coordinates']['latitude'])
        # print(cinema['coordinates']['longitude'])
        # print(cinema['address'])
        # print(phones[0])
        # print(phones[1])
        # print(phones[2])
        # print(metro_stations.id)
        # print('++++++++++++++++++++++++++++++++')
        print('Парсим всю инфу по кт - {}'.format(cinema['title']))
        get_or_create(db_session, MovieTheaters,
                      metro_id=metro_st_id,
                      yandex_theater_id=cinema['id'],
                      title=cinema['title'],
                      latitude=cinema['coordinates']['latitude'],
                      longitude=cinema['coordinates']['longitude'],
                      address=cinema['address'],
                      description="",
                      phone1=phones[0],
                      phone2=phones[1],
                      phone3=phones[2])
        # exit()


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


def get_closest_metro_station(data, latitude, longitude):
    return min(data, key=lambda data: get_distance(latitude, longitude, data['latitude'], data['longitude']))


def get_distance(x1, y1, point_x1, point_y1):
    return sqrt((x1 - point_x1) ** 2 + (y1 - point_y1) ** 2)


def check_movie_in_db():
    test_url_movie_list = 'https://afisha.yandex.ru/api/events/actual?' \
                          'limit=12&offset=12&tag=cinema&hasMixed=0&date=' + str(date.today()) + '&period=1&city=moscow'
    movie_list = get_json_from_url(test_url_movie_list)
    for i in range(int(movie_list['paging']['total'] / 12 + 1)):
        # date_for_url = str(date.today() + timedelta(0))
        url_movie_list = 'https://afisha.yandex.ru/api/events/actual?limit=12&offset='+str(i*12)+'&tag=cinema' \
                         '&hasMixed=0&date='+str(date.today())+'&period=1&city=moscow'
        movie_list = get_json_from_url(url_movie_list)
        for movie in movie_list['data']:
            # print(json.dumps(movie, sort_keys=True, indent=4, ensure_ascii=False))
            print('Парсим фильм {}'.format(movie['event']['title']))
            get_or_create(db_session, Movies,
                          yandex_movie_id=movie['event']['id'],
                          title=movie['event']['title'],
                          start_date=movie['scheduleInfo']['dateReleased'],
                          rating=str(movie['rank']))


def get_raw_page_from_afisha_yandex(url):
    # return BeautifulSoup(urlopen('https://www.afisha.ru/msk/cinema/').read(), "lxml")
    return BeautifulSoup(urlopen(url).read(), "lxml")


def get_title_from_page(soup):
    return True


def get_year_from_page(soup):
    return True


def get_director_from_page(soup):
    return True


def get_cast_from_page(soup):
    return True


def get_movie_info(query):
    raw_page = get_raw_page_from_afisha_yandex(query)
    soup = BeautifulSoup(raw_page)

    title = get_title_from_page(soup)
    year = get_year_from_page(soup)
    director = get_director_from_page(soup)
    cast_list = get_cast_from_page(soup)

    return {
        'title': title,
        'year': year,
        'director': director,
        'cast_list': cast_list,
    }


get_or_create(db_session, MovieFormats, title="2D")
get_or_create(db_session, MovieFormats, title="3D")


def main():
    # pass
    # check_metro_in_db()
    # check_cinema_in_db()
    check_movie_in_db()
    # test test test
    # test for commit


if __name__ == '__main__':
    main()
