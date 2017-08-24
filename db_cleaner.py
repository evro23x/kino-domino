from db_schema import MovieTheaters, Movies, db_session, TimeSlots, MovieFormats
from sqlalchemy import func


def get_duplicate_movie_theater_id():
    # Ищем все дублирующие записи в таблице MovieTheaters
    duplicates = (
        db_session.query(
            func.count(), MovieTheaters.title
        ).group_by(MovieTheaters.title).having(func.count() > 1)
    ).all()

    # Получаем id дубликатов, для последующего обновления таблицы Movies и удаления дубликатов из MovieTheaters
    for duplicate in duplicates:
        duplicate_ids = db_session.query(MovieTheaters.id).filter(MovieTheaters.title == duplicate[1]).all()
        # print(duplicate_ids)
        # print(duplicate_ids[0][0])
        # print(duplicate_ids[1][0])

        print("First movie theater id = {} \nSecond movie theater id = {} ".format(duplicate_ids[0][0],
              duplicate_ids[1][0]))

    exit(0)

    return duplicates


def update_movie_theater_id_in_movies_table():
    return True


if __name__ == '__main__':
    mt_id = get_duplicate_movie_theater_id()
    # update_movie_theater_id_in_movies_table(mt_id)

    # делаем выборку из таблицы movie_theaters по title если совпадений больше 1
    # разбираем получившийся массив одномерных массивов по нулевому ключу
    # обновляем таблицу time_slots, в поле movie_theaters_id меняем на второе значение из массива дублей
    # удаляем кт из первого списка
    # удаляем кт по id из таблицы movie_theaters

    # !!! Обязательно доделать это, очень важный и критический таск. !!!
