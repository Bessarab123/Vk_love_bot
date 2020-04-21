from data.user import *


def get_last_message(db_session, user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return ""
    return user.last_message


def get_interlocutor(db_session, user_id):
    """Возращает id собеседника"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return ""
    return user.interlocutor


def get_description(db_session, user_id):
    """Возращает по id анкету собеседника"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return ""
    return user.description

def get_user(db_session, user_id):
    """Возращает пользователя как объект таблицы"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return ""
    return user

def get_user_info(db_session, user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return ""
    return {"age": user.age, "city": user.city, "sex": user.sex, "description": user.description}


def update_user_data(db_session, user_id, dictionary={}):
    """Изменить данные в БД или добавить пользователя в БД

    db_session - говорит сам за себя, сэссия БД
    user_id - id пользователя vk и в БД, если его нет в БД, то создаёт его
    dictionary - словарь, обрабатываются только ключи: last_text, scores, city,
    age, sex, description - со значением в виде строки, кроме scores приходящем в виде числа
    """
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        user = User()
        user.vk_id = user_id
        user.scores = 500
        session.add(user)
    for key in dictionary.keys():
        if key == "last_text":
            user.last_message = dictionary[key]
        elif key == "scores":
            user.scores += dictionary[key]
        elif key == "city":
            user.city = dictionary[key]
        elif key == "age":
            user.age = dictionary[key]
        elif key == "sex":
            user.sex = dictionary[key]
        elif key == "description":
            user.description = dictionary[key]
        elif key == "interlocutor":
            user.interlocutor = dictionary[key]
    session.commit()
