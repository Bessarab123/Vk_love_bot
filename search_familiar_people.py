from data.user import User
from update_data import get_user


def search_for_familiar_people(db_session, user, age_interlocutor=None,
                               city_interlocutor=None, sex_interlocutor=None, rout=1):
    """Ищем пользователей по критериям
    user - пользователь из таблицы
    age, city, sex - атрибуты для ограничения поиска"""
    session = db_session.create_session()
    scores = user.scores
    rout -= 1
    age, city, sex = (age_interlocutor if age_interlocutor else user.age, city_interlocutor if
    city_interlocutor else user.city, sex_interlocutor if sex_interlocutor else user.sex)
    for i in range(rout, 4):
        age_dif = i * 10 + 2
        if not i:
            interlocutors = get_from_db_interlocutors(session, user, age, age_dif, sex, city)
            if interlocutors:
                return (list(map(lambda x: x.vk_id, interlocutors)), i + 1)
        elif i == 1:
            interlocutors = get_from_db_interlocutors(session, user, age, age_dif, sex)
            if interlocutors:
                return (list(map(lambda x: x.vk_id, interlocutors)), i + 1)
        elif i == 2:
            interlocutors = get_from_db_interlocutors(session, user, age, age_dif)
            if interlocutors:
                return (list(map(lambda x: x.vk_id, interlocutors)), i + 1)
        elif i == 3:
            age_dif = 100
            interlocutors = get_from_db_interlocutors(session, user, age, age_dif)
            return (list(map(lambda x: x.vk_id, interlocutors)), i + 1)


def get_from_db_interlocutors(session, user, age, age_dif=2, sex=None, city=None):
    scores_dif = 200
    max_age = user.age + age_dif
    min_age = user.age - age_dif
    return list(session.query(User).filter((User.scores >= user.scores - scores_dif) |
                                           (User.scores <= user.scores + scores_dif),
                                           User.interlocutor == None, User.in_group == True,
                                           User.vk_id != user.vk_id,
                                           ((User.city == city) if city else User.city.like('%%')),
                                           ((User.sex == sex) if sex else User.sex.in_(['М', 'Ж'])),
                                           (max_age > User.age) | (User.age > min_age)
                                           ))
