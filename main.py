import vk_api
import json
from data import db_session


def get_vk_session(user=True):
    def auth_handler():
        """ При двухфакторной аутентификации вызывается эта функция. """
        key = input("Enter authentication code: ")
        remember_device = 'Y' in input("Remeber? Y/N :")
        return key, remember_device

    if user:
        # Взять session юзера
        with open("pass.json") as f:
            data = json.load(f)
            password = data["password"]
            login = data["login"]
        vk_session = vk_api.VkApi(password, login, auth_handler=auth_handler)
        try:
            vk_session.auth()
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return
    else:
        # Взять session группы
        with open("pass.json") as f:
            data = json.load(f)
            api = data["api"]
        vk_session = vk_api.VkApi(
            token=api)
    return vk_session


if __name__ == '__main__':
    db_session.global_init("vk_love_bot.db")
    vk_session = get_vk_session(True)
    vk = vk_session.get_api()
    # TODO тут что-то должно появиться
