from main import *


def search_for_familiar_people(user):
    session = db_session.create_session()
    age = user.age
    if age is None:
        age = 16
    city = user.city
    if city is None:
        city = 'Тула'
    friends = []
    for friend in session.query(User).filter(User.age >= age - 1, User.age <= age + 1, User.city == city):
        friends.append(friend)
    return friends
