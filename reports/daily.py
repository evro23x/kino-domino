from db_schema import db_session, Movies
from datetime import datetime


# Добавлено кт
def new_movie_theaters():
    return 0


# Добавлено фильмов
def new_movies():
    return 0


# Добавлено сеансов
def new_time_slots():
    return 0


# Премьеры = N
def new_movie_premier():
    return 0


# собираем отчет
def total_report():
    report = {'movie_theaters': new_movie_theaters(),
              'new_movies': new_movies(),
              'new_time_slots': new_time_slots(),
              'new_movie_premier': new_movie_premier()}
    return report


def main():
    print(total_report())


if __name__ == '__main__':
    main()
