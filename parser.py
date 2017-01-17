from bs4 import BeautifulSoup
from urllib.request import urlopen
from db_schema import db_session, MetroStations, MovieTheaters, TimeSlots, Movies, MovieFormats
from datetime import datetime, date, time

COUNTER = 0
ITERATIONS = 3
# today = date.today()
# while COUNTER < ITERATIONS:
#     today = date.today()
#     my_birthday = date(today.year, today.month, day=today.day + COUNTER)
#     print(type(my_birthday))
#     print(str(my_birthday))
#     print(my_birthday)
#     print(COUNTER)
#     COUNTER += 1
# exit(0)
#


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


get_or_create(db_session, MovieFormats, title="2D")
get_or_create(db_session, MovieFormats, title="3D")

html_doc = urlopen('https://www.afisha.ru/msk/cinema/').read()
soup = BeautifulSoup(html_doc, "lxml")
try:
    for li in soup.find('ul', {'class': 'b-dropdown-common-fixed'}).findAll('li'):
        metro = get_or_create(db_session, MetroStations,
                              title=str(li.find('a').contents[0]),
                              latitude="0",
                              longitude="0")

        # print('https:{}'.format(li.find('a')['href']))
        metro_to_cinema = BeautifulSoup(urlopen('https:' + li.find('a')['href']).read(), 'lxml')
        for div_cinema in metro_to_cinema.find('div', {'class': 'b-places-list'}).findAll('h3'):
            movie_title = str(div_cinema.find('a').contents[0])
            theater = get_or_create(db_session, MovieTheaters,
                                    metro_id=metro.id,
                                    title=movie_title,
                                    latitude="0",
                                    longitude="0",
                                    adress="",
                                    description="",
                                    phone="", )

            # print("Парсим - {}".format(movie_title))
            pattern_url_table = 'https://www.afisha.ru/msk/schedule_cinema_place/'
            url_cinema = div_cinema.find('a')['href']
            id_cinema = url_cinema[url_cinema[0:-1].rfind('/') + 1:-1]

            counter = 0

            while counter < ITERATIONS:
                session_date = date(date.today().year, date.today().month, day=date.today().day + counter)

                date_for_url = '/' + str(session_date.day) + \
                               '-' + str(session_date.month) + \
                               '-' + str(session_date.year) + '/'
                print("Парсим - {} за {} число".format(movie_title, date_for_url))

                url_table = pattern_url_table + id_cinema + date_for_url

                link_to_cinema = BeautifulSoup(urlopen(url_table).read(), 'lxml')
                # print("?? - {}".format(pattern_url_table))
                # print("?? - {}".format(url_cinema))
                # print("?? - {}".format(id_cinema))
                # print("?? - {}".format(url_table))
                # print("?? - {}".format(link_to_cinema))
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
                except AttributeError:
                    print("exception AttributeError")

                # if movie_title == 'Олимпик Синема':
                #     exit(0)

                counter += 1

except KeyboardInterrupt:
    print()
