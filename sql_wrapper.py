from db_schema import db_session, BotLog, Movies
from datetime import datetime


def get_or_create(current_session, model, **kwargs):
    """
    Получить либо создать

    Функция получения данных из базы по передаваемым параметрам.
    Создает новую запись в базе если запрашиваемый отбъект отсуствует.
    """
    instance = current_session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        current_session.add(instance)
        current_session.commit()
        return instance


def add_log(update, msg_in='', msg_out=''):
    user_telegram_id = update.message.chat.id
    user_telegram_name = update.message.chat.first_name + ' ' + update.message.chat.last_name

    instance = BotLog(datetime.today(), user_telegram_id, user_telegram_name,  msg_in, msg_out)
    db_session.add(instance)
    db_session.commit()


def reset_movies_status():
    db_session.query(Movies).update({"movie_status": 0})
    db_session.commit()


def get_premier_dict():
    return db_session.query(Movies).filter_by(movie_status=1).all()
