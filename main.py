import random
from pprint import pprint

import vk_api
import json
from data import db_session

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


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


def message():
    pprint(media)
    if media['attachments'][0]['type'] == 'audio_message':
        id = media['attachments'][0]['audio_message']['id']
        access_key = media['attachments'][0]['audio_message']['access_key']
        vk.messages.send(user_id=user, attachment=f'audio_message{user}_{id}_{access_key}',
                         random_id=random.randint(0, 2 ** 64))
    elif False:
        pass
    else:
        id = media['attachments'][0]['photo']['id']
        access_key = media['attachments'][0]['photo']['access_key']

        vk.messages.send(user_id=user,
                         attachment=f'photo{user}_{id}_{access_key}',
                         random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    vk_session = get_vk_session(False)
    db_session.global_init("vk_love_bot.db")
    longpoll = VkBotLongPoll(vk_session, 193209431)
    if 'Y' == input('Запуск Бота? Y/N'):
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:

                vk = vk_session.get_api()
                user = vk.users.get(user_ids=event.obj.message['from_id'])[0]['id']
                print(user)
                media = event.obj.message
                # СДЕСЬ ФУНКЦИЯ КОТОРАЯ ОБРАБАЫТВЕТ СООБЩЕНИЯ И ГОТОВА ИХ ОТПРАЛЯТЬ message()

