from bs4 import BeautifulSoup
from urllib.request import urlopen
from db_schema import db_session, MetroStations, MovieTheaters, TimeSlots, Movies, MovieFormats
from datetime import datetime, date, time

# d = date(2005, 7, 14)
# t = time(12, 30)
# print(datetime.combine(d, t).timestamp())


# print(time.time())
# print(datetime.datetime.now(""))
exit()
# me = MetroStations("Таганская", "55.7796266", "37.5992518")
# db_session.add(me)
# db_session.commit()


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


html_doc = urlopen('https://www.afisha.ru/msk/cinema/').read()
soup = BeautifulSoup(html_doc, "lxml")

for li in soup.find('ul', {'class': 'b-dropdown-common-fixed'}).findAll('li'):

    metro = get_or_create(db_session, MetroStations,
                          title=str(li.find('a').contents[0]),
                          latitude="0",
                          longitude="0")

    # print(metro.id)

    metro_to_cinema = BeautifulSoup(urlopen('https:' + li.find('a')['href']).read(), 'lxml')
    for div_cinema in metro_to_cinema.find('div', {'class': 'b-places-list'}).findAll('h3'):

        theater = get_or_create(db_session, MovieTheaters,
                                metro_id=metro.id,
                                title=str(div_cinema.find('a').contents[0]),
                                latitude="0",
                                longitude="0",
                                adress="",
                                description="",
                                phone="", )

        # print(theater.id)

        print("Парсим - {}".format(str(div_cinema.find('a').contents[0])))
        pattern_url_table = 'https://www.afisha.ru/msk/schedule_cinema_place/'
        url_cinema = div_cinema.find('a')['href']
        id_cinema = url_cinema[url_cinema[0:-1].rfind('/') + 1:-1]
        url_table = pattern_url_table + id_cinema + '/'
        link_to_cinema = BeautifulSoup(urlopen(url_table).read(), 'lxml')
        film_name_saver = ""
        # проверка необходима чтобы парсер на валился на 3D фильмах
        try:
            # парсим фильмы и сеансы со страницы определенного кт
            for div_film in link_to_cinema.find('div', {'class': 'b-theme-schedule'}).findAll('tr'):
                # собираем сеансы в один список для удобство отображения в терминале
                # print(div_film)

                session_list = []
                movie_format_3d = False
                # print("==================================================================== start")
                for session in div_film.find('div', {'class': 'time-inside line'}).findAll('span'):

                    # print("Название фильма = ".format(
                    #     str(div_film.find('div', {'class': 'clearfix'}).find('a').contents[0])))

                    session_clear = ' '.join(session.contents[0].replace(' ', '').split())
                    # костылим и хардкодим, у сеанса есть три состояния, разберем по порядку
                    # 1 - сеанс прошел и на него нельзя купить билеты
                    # 2 - сеанс будет но на него нельзя купить билеты
                    # 3 - сеанс будет  и на него можно  купить билеты
                    if str(session).find("inactive") == 13:
                        session_list.append(session_clear)
                    elif str(session).find("href") == 10:
                        session_list.append(session.find("a").contents[0])
                    else:
                        session_list.append(session_clear)

                if str(div_film.find('span', {'class': 'title'})).find("Сеансы в формате") == 20 and str(
                        div_film.find('div', {'class': 'clearfix'})) == "None":
                    # film_name_saver = str(div_film.find('div', {'class': 'clearfix'}).find('a').contents[0])
                    session_list.remove("Сеансывформате")

                    # print("Название фильма: {} в формате 3D - {}".format(film_name_saver, session_list))
                    movie_format_3d = True
                    note1 = "Название фильма: " + film_name_saver + "в формате 3D - "
                    note2 = str(session_list) + "\n"

                    # film_name_saver = ""
                else:
                    film_name_saver = str(div_film.find('div', {'class': 'clearfix'}).find('a').contents[0])
                    # print("Название фильма: {} - {}".format(film_name_saver, session_list))
                    note1 = "Название фильма: " + film_name_saver + " - "
                    note2 = str(session_list) + "\n"

                # print(film_name_saver)
                # if movie_format_3d:
                #     print("3D format")
                # print(type(session_list))
                movie = get_or_create(db_session, Movies, title=film_name_saver)
                for session in session_list:
                    # int(datetime.datetime.strptime('01/12/2011', '%d/%m/%Y').strftime("%s"))

                    time_slots = get_or_create(db_session, TimeSlots,
                                               time=session,
                                               movie_theaters_id=theater.id,
                                               movie_id=movie.id)

                # if str(div_film.find('div', {'class': 'clearfix'})) == "None":
                # print("==================================================================== start")
                # print(film_name_saver)
                #     print(div_film)
                # print("---- {}".format(str(div_film.find('div', {'class': 'clearfix'}))))
                # print(str(div_film.find('span', {'class': 'title'})).find("Сеансы в формате"))
                # print("====================================================================   end")
                # разбираем верстку, удаляя лишний html и спец_символы
                # exit(0)

        except AttributeError:
            print("exception AttributeError")
            # exit(0)
    exit(0)
