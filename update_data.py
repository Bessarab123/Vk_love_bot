from main import *
from data.user import *


def get_last_message(db_session, user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return ""
    return user.last_message


def update_user_data(db_session, user_id, dictionary={}):
    session = db_session.create_session()
    user = session.query(User).filter(User.vk_id == user_id)
    print(user) # TODO не могу ни создать польозвателя ни проверить его наличие
    if not user:
        user = User()
        user.vk_id = user_id
        user.scores = 500
        session.add(user)
    for key in dictionary.keys():
        if key == "city":
            user.city = dictionary[key]
        elif key == "age":
            user.age = dictionary[key]
        elif key == "sex":
            user.sex = dictionary[key]
        elif key == "description":
            user.description = dictionary[key]
    session.commit()
