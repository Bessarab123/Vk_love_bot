from data.user import *
from datetime import date


class ErrorGetData(Exception):
    pass


def get_last_message(db_session, user_id):
    """Возращает последние сообщение пользователя по id
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        raise ErrorGetData
    return user.last_message


def get_interlocutor(db_session, user_id):
    """Возращает id собеседника или None
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        raise ErrorGetData
    return user.interlocutor


def get_description(db_session, user_id):
    """Возращает по id анкету собеседника
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        raise ErrorGetData
    return user.description


def get_user(db_session, user_id):
    """Возращает пользователя как объект таблицы
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        raise ErrorGetData
    return user


def get_user_info(db_session, user_id) -> dict:
    """Возращает доп. информацию о пользователе по id
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        raise ErrorGetData
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
        # Если нет пользоваетеля то его создаем
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


def create_data_user(db_session, user_id, vk):
    """Собарть данные пользователя из vk по его id """
    # Получаем из профиля пользователя данные о нём
    data = vk.users.get(user_ids=user_id, fields='city, bdate, sex')[0]
    if data['sex'] == 1:
        sex = 'Женский'
    elif data['sex'] == 2:
        sex = 'Мужской'
    else:
        sex = 'Не указан'

    if 'city' in data.keys():
        city = data['city']['title']
    else:
        city = 'Не указан'

    if 'bdate' in data.keys():
        today = date.today()
        day, month, year = tuple(map(int, data['bdate'].split('.')))
        age = str(today.year - year - ((today.month, today.day) < (month, day)))
    else:
        age = 'Не указан'
    # Обновляем базу данных
    update_user_data(db_session, user_id, {"sex": sex, "age": age, "city": city})
    print('Создание пользователя...', user_id, sex, age, city)


def update_db(db_session, vk):
    """Обновить базу данных всзязи с непостоянностью жизни"""
    session = db_session.create_session()
    for user in session.query(User).all():
        create_data_user(db_session, user.vk_id, vk)
    print("База данных обновлена")
