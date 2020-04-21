from main import *


def search_for_familiar_people(db_session, user, age, city, sex):
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
        if friend.vk_id != user.vk_id and (friend.city == city or city is None) and (friend.sex == sex or sex is None):
            friends.append(friend.vk_id)
    return friends
