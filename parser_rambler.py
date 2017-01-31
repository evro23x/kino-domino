from bs4 import BeautifulSoup
from urllib.request import urlopen
from db_schema import db_session, MetroStations, MovieTheaters, TimeSlots, Movies, MovieFormats
from datetime import datetime, date, time, timedelta

COUNTER = 0
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


get_or_create(db_session, MovieFormats, title="2D")
get_or_create(db_session, MovieFormats, title="3D")

soup = BeautifulSoup(urlopen('https://www.afisha.ru/msk/cinema/').read(), "lxml")
try:
    for li in soup.find('ul', {'class': 'b-dropdown-common-fixed'}).findAll('li'):
        metro = get_or_create(db_session, MetroStations,
                              title=str(li.find('a').contents[0]),
                              latitude="0",
                              longitude="0")

        metro_to_cinema = BeautifulSoup(urlopen('https:' + li.find('a')['href']).read(), 'lxml')
        for div_cinema in metro_to_cinema.findAll('div', {'class': 'places-list-item'}):

            movie_title = str(div_cinema.find('h3').find('a').contents[0])
            cinema_info = ' '.join(div_cinema.find('div', {'class': 'places-address'}).contents[0].split())

            phone1 = ''
            phone2 = ''
            phone3 = ''
            address = ''

            if cinema_info[0] == "+":
                phone1 = cinema_info[:cinema_info.find(',')]
                address = cinema_info[cinema_info.find(',') + 2:]
                if address[0] == "+":
                    phone2 = address[:address.find(',')]
                    address = address[address.find(',') + 2:]
                    if address[0] == "+":
                        phone3 = address[:address.find(',')]
                        address = address[address.find(',') + 2:]
            else:
                address = cinema_info

            theater = get_or_create(db_session, MovieTheaters,
                                    metro_id=metro.id,
                                    title=movie_title,
                                    latitude="0",
                                    longitude="0",
                                    address=address,
                                    description="",
                                    phone1=phone1,
                                    phone2=phone2,
                                    phone3=phone3)

            counter = 0
            while counter < ITERATIONS:
                session_date = date.today() + timedelta(counter)
                url_time_slot = str(div_cinema.find('a')['href']).replace('/cinema/', '/schedule_cinema_place/')
                url_table = 'http:' + url_time_slot + session_date.strftime('%d-%m-%Y')
                link_to_cinema = BeautifulSoup(urlopen(url_table).read(), 'lxml')
                film_name_saver = ""
                # проверка необходима чтобы парсер не валился на 3D фильмах
                try:
                    # парсим фильмы и сеансы со страницы определенного кт
                    for div_film in link_to_cinema.find('div', {'class': 'b-theme-schedule'}).findAll('tr'):
                        # собираем сеансы в один список для удобство отображения в терминале
                        movie_format_3d = False

                        if str(div_film.find('span', {'class': 'title'})).find("Сеансы в формате") == 20 and str(
                                div_film.find('div', {'class': 'clearfix'})) == "None":
                            movie_format_3d = True
                        else:
                            film_name_saver = str(div_film.find('div', {'class': 'clearfix'}).find('a').contents[0])
                        movie = get_or_create(db_session, Movies, title=film_name_saver)

                        for session in div_film.find('div', {'class': 'time-inside line'}).findAll('span'):
                            session_clear = ' '.join(session.contents[0].replace(' ', '').split())
                            # костылим и хардкодим, у сеанса есть три состояния, разберем по порядку
                            # 1 - сеанс прошел и на него нельзя купить билеты
                            # 2 - сеанс будет но на него нельзя купить билеты
                            # 3 - сеанс будет  и на него можно  купить билеты
                            # PS: после переезда на бой и настройки крона на ежедневный запуск в полночь
                            # код ниже утратит актуальность, так как все фильмы будут активны
                            if str(session).find("inactive") == 13:
                                time_str = session_clear
                            elif str(session).find("href") == 10:
                                time_str = session.find("a").contents[0]
                            else:
                                if session_clear == "Сеансывформате":
                                    continue
                                time_str = session_clear

                            # Проверка ниже отметает варианты когда в строке время сеанса прилетает рандомный текст
                            if len(time_str) > 6:
                                continue

                            hour, minute = [int(info) for info in time_str.split(':')]
                            session_time = time(hour, minute)

                            format_id = 2 if movie_format_3d else 1

                            time_slots = get_or_create(db_session, TimeSlots,
                                                       movie_theaters_id=theater.id,
                                                       movie_id=movie.id,
                                                       movie_formats_id=format_id,
                                                       time=datetime.combine(session_date, session_time))

                    print("Парсим - {}, на - {} - success".format(movie_title, session_date.strftime('%d-%m-%Y')))
                except AttributeError:
                    print("Парсим - {}, на - {} - fail".format(movie_title, session_date.strftime('%d-%m-%Y')))
                counter += 1
except KeyboardInterrupt:
    print()
