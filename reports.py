from db_schema import db_session, MetroStations, Movies, MovieTheaters, TimeSlots
from datetime import datetime, date, timedelta
from sql_wrapper import get_premier_dict
from config import gmail_sender, gmail_passwd
import smtplib


# Добавлено станций метро
def new_metro_station():
    return len(db_session.query(MetroStations).filter_by(created_time=date.today()).all())


# Добавлено кт
def new_movie_theaters():
    return len(db_session.query(MovieTheaters).filter_by(created_time=date.today()).all())


# Добавлено фильмов
def new_movies():
    return len(db_session.query(Movies).filter_by(create_date=date.today()).all())


# Добавлено сеансов
def new_time_slots():
    sessions = db_session.query(TimeSlots).filter(
        TimeSlots.time > date.today(), TimeSlots.time < (date.today() + timedelta(days=1))
    ).all()
    return len(sessions)


# Премьеры
def new_movie_premier():
    # movies_dict = get_premier_dict()
    # premier_info = "Премьеры недели:\n\n"
    # for movie_obj in movies_dict:
    #     premier_info += movie_obj.title
    #     if movie_obj.trailer_url:
    #         premier_info += " - <a href='" + movie_obj.trailer_url + "'>трейлер</a>\n"
    #     else:
    #         premier_info += "\n"
    return len(get_premier_dict())


# собираем отчет
def total_report():
    report_date = datetime.today().strftime('%Y-%m-%d %H:%M')
    report = 'Parser kino-domino finish work in {}, new data in db : \r\n'.format(report_date)
    report += 'metro station = {}, \r\ntheatres = {}, \r\nmovies = {}, \r\nsession = {}, \r\npremier = {}'.format(
        new_metro_station(),
        new_movie_theaters(),
        new_movies(),
        new_time_slots(),
        new_movie_premier()
    )
    return report


# отправляем электрописьмо
def send_report_mail():
    TO = 'evro23x@mail.ru'
    SUBJECT = 'Kino-domino: parser result information {}'.format(date.today())
    TEXT = total_report()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)

    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', TEXT])
    try:
        server.sendmail(gmail_sender, [TO], BODY)
        print('email sent')
    except:
        print('error sending mail')
    server.quit()


def main():
    pass


if __name__ == '__main__':
    main()
