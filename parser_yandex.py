from math import sqrt

from bs4 import BeautifulSoup
from urllib.request import urlopen
from db_schema import db_session, MetroStations, MovieTheaters, TimeSlots, Movies, MovieFormats
# from datetime import datetime, date, time
import requests

ITERATIONS = 3


# print(db_session.query(MetroStations).all())

# for instance in db_session.query(MetroStations).order_by(MetroStations.id):
#     print(instance.id, instance.title, instance.latitude, instance.longitude)
# print(MetroStations.query.filter().all())


# exit(0)


def get_or_create(current_session, model, **kwargs):
    instance = current_session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        current_session.add(instance)
        current_session.commit()
        return instance


def get_list_metro_station():
    return requests.get('https://api.hh.ru/metro/1').json()


def check_metro_in_db():
    for metro in get_list_metro_station()['lines']:
        print(metro['name'])
        for station in metro['stations']:
            get_or_create(db_session, MetroStations,
                          title=station['name'],
                          latitude=station['lat'],
                          longitude=station['lng'])


def get_list_cinema():
    payload = {'limit': 200, 'offset': 0, 'city': 'moscow'}
    return requests.get('https://afisha.yandex.ru/api/events/cinema/places', params=payload).json()['items']


def check_cinema_in_db():
    for cinema in get_list_cinema():
        if cinema['phones'] and len(cinema['phones']) != 0:
            phone1 = cinema['phones'][0]['numbers']
        else:
            phone1 = ''

        if cinema['metro'] and len(cinema['metro']) != 0:
            metro_stations = MetroStations.query.filter(
                MetroStations.title.ilike("%{}%".format(cinema['metro'][0]['name']))).first()
        else:
            metro_stations = get_closest_metro(get_list_metro_station(),
                                               cinema['coordinates']['latitude'], cinema['coordinates']['longitude'])
            print(metro_stations)

        print(phone1)
        # print(metro_stations.id)
        print('++++++++++++++++++++++++++++++++')
        # break
        # print(cinema['coordinates']['latitude'])
        # print(cinema['coordinates']['longitude'])
        # break
        #
        # get_or_create(db_session, MovieTheaters,
        #               metro_id=metro_id,
        #               title=cinema['title'],
        #               latitude=cinema['coordinates']['latitude'],
        #               longitude=cinema['coordinates']['longitude'],
        #               address=cinema['address'],
        #               description="",
        #               phone1=phone1)


def get_closest_metro(data, latitude, longitude):
    return min(data, key=lambda data: get_distance(latitude, longitude, data['coordinates']))


def get_distance(x1, y1, point):
    return sqrt((x1 - point[0]) ** 2 + (y1 - point[1]) ** 2)


def get_count_ajax_pages(url):
    pass


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
    # check_metro_in_db()
    check_cinema_in_db()


if __name__ == '__main__':
    main()
