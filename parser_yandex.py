from bs4 import BeautifulSoup
from urllib.request import urlopen
from db_schema import db_session, MetroStations, MovieTheaters, TimeSlots, Movies, MovieFormats
from datetime import datetime, date, time
# from requets

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
    theaters_list_page = get_raw_page_from_afisha_yandex("https://afisha.yandex.ru/events/cinema/places?city=moscow&page=11")
    for theater in theaters_list_page.findAll('div', {'class': 'place-card places-list__item content-places__item'}):
        print(theater.find('h2', {'class': 'place-card__title'}).contents[0])


if __name__ == '__main__':
    main()