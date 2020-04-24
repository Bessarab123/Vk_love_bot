from data.user import *
from update_data import get_user


def search_for_familiar_people(db_session, user, age, city, sex):
    """Ищем пользователей по критериям
    user - пользователь из таблицы
    age, city, sex - атрибуты для ограничения поиска"""
    session = db_session.create_session()
    scores = user.scores
    age_dif = 1
    scores_dif = 100
    if age is None:
        age = user.age
    if city is None:
        city = user.city
    if age is None:
        age = 100
        age_dif = 100
    if scores is None:
        scores = 100000
        scores_dif = 10000
    friends = []
    for friend in session.query(User).filter(User.age >= age - age_dif, User.age <= age + age_dif,
                                             User.scores >= scores - scores_dif,
                                             User.scores <= scores + scores_dif):
        if friend.vk_id != user.vk_id and (friend.city == city or city is None) and (friend.sex == sex or sex is None) \
                and friend.interlocutor is None:
            friends.append(friend.vk_id)
    return friends

def get_interlocutor_list(db_session, user_id):
    session = db_session.create_session()

    user = get_user(db_session, user_id)
    #for a in session.query(User).get(user.vk_id):
    #    print(a)
    return []