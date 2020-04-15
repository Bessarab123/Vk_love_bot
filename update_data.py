from main import *
from data.user import *


def update_data(db_session, user_id, dictionary={}):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        user = User(vk_id=user_id)
        session.add(user)
    for key in dictionary:
        if key == "city":
            user.city = dictionary[key]
        elif key == "age":
            user.age = dictionary[key]
        elif key == "sex":
            user.sex = dictionary[key]
        elif key == "description":
            user.description = dictionary[key]
    session.commit()
