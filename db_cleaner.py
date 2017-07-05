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
        print(duplicate_ids)
    exit(0)

    return duplicates


def update_movie_theater_id_in_movies_table():
    return True


if __name__ == '__main__':
    mt_id = get_duplicate_movie_theater_id()
    # update_movie_theater_id_in_movies_table(mt_id)
