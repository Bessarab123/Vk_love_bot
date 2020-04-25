import datetime
import json
import vk_api
from log import log_to_file_info_DB_news_of_users, log_to_file_error_with_DB, log_ban_user, \
    log_to_file_update_DB

from data.user import *


class ErrorGetData(Exception):
    pass


class InputInfoUserError(Exception):
    pass


def get_last_message(db_session, user_id):
    """Возращает последние сообщение пользователя по id
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    user = get_user(db_session, user_id)
    return user.last_message


def get_interlocutor(db_session, user_id):
    """Возращает id собеседника или None
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    user = get_user(db_session, user_id)
    return user.interlocutor


def get_description(db_session, user_id):
    """Возращает по id анкету собеседника
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    user = get_user(db_session, user_id)
    return user.description


def get_score(db_session, user_id):
    """Возращает очки пользователя по id
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    user = get_user(db_session, user_id)
    return user.scores


def get_user(db_session, user_id):
    """Возращает пользователя как объект таблицы
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.close()
    if not user:
        log_to_file_error_with_DB()
        raise ErrorGetData
    return user


def get_user_info(db_session, user_id) -> str:
    """Возращает доп. информацию о пользователе по id
    db_session - сэссия БД
    user_id - id пользователя vk и в БД"""
    user = get_user(db_session, user_id)
    return f"Возраст {user.age}, пол: {user.sex}, Город: {user.city}, Вот его анкета:" \
           f" {user.description}\n"


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
        session.add(user)
    for key in dictionary.keys():
        if key == "last_text":
            user.last_message = dictionary[key]
        elif key == "in_group":
            user.in_group = dictionary[key] if dictionary[key] != None else user.in_group
        elif key == "description":
            user.description = dictionary[key]
        elif key == "scores":
            user.scores += dictionary[key]
        elif key == "interlocutor":
            user.interlocutor = dictionary[key]
        elif key == "city":
            user.city = dictionary[key]
        elif key == "age":
            user.age = dictionary[key]
        elif key == "sex":
            user.sex = dictionary[key]
    session.commit()


def create_data_user(db_session, user_id, vk, goin=None):
    """Собарть данные пользователя из vk по его id
    db_session - сэссия БД
    user_id - id пользователя vk и в БД
    vk - vk_api.vk_api.VkApiMethod
    goin - флагш на который нужно изменить значение в таблице"""
    # Получаем из профиля пользователя данные о нём
    data = vk.users.get(user_ids=user_id, fields='city, bdate, sex')[0]
    if data['sex'] == 1:
        sex = 'Ж'
    elif data['sex'] == 2:
        sex = 'М'
    else:
        sex = 'Не указан'

    if 'city' in data.keys():
        city = data['city']['title']
    else:
        city = 'Не указан'

    if 'bdate' in data.keys():
        today = datetime.date.today()
        if len(tuple(map(int, data['bdate'].split('.')))) != 3:
            age = 'Не указан'
        else:
            day, month, year = tuple(map(int, data['bdate'].split('.')))
            age = str(today.year - year - ((today.month, today.day) < (month, day)))
    else:
        age = 'Не указан'
    # Обновляем базу данных
    update_user_data(db_session, user_id, {"sex": sex, "age": age, "city": city, "in_group": goin})
    log_to_file_info_DB_news_of_users(user_id)


def update_db(db_session, vk):
    """Обновить базу данных всзязи с непостоянностью жизни у кого-то день рождения, а кого-то
    пора выгнать"""
    session = db_session.create_session()
    log_to_file_update_DB()
    for user in session.query(User).all():
        create_data_user(db_session, user.vk_id, vk)
        update_user_data(db_session, user.vk_id, {"scores": int(-user.scores * 0.1)})
        if user.scores < -500:
            vk_u = get_vk_session_user()
            unixtime = int(datetime.datetime.now().timestamp()) + 3600 * (user.scores + 500) * -1
            vk_u.groups.ban(group_id=193209431, owner_id=user.vk_id, end_date=unixtime,
                            comment="Вы имеете слишком мало очков", comment_visible=1)
            log_ban_user(user.vk_id, datetime.datetime.fromtimestamp(unixtime))


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """
    key = input("Enter authentication code: ")
    remember_device = 'Y' in input("Remeber? Y/N :")
    return key, remember_device


def get_vk_session_user():
    with open("pass.json") as f:
        data = json.load(f)
        password = data["password"]
        login = data["login"]
    vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
    return vk_session.get_api()
