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
