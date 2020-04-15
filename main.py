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


def message(media, user):
    if media['attachments'][0]['type'] == 'audio_message':
        id = media['attachments'][0]['audio_message']['id']
        access_key = media['attachments'][0]['audio_message']['access_key']
        vk.messages.send(user_id=user, message=media['attachments'][0]['audio_message']['link_mp3'],
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
    vk = vk_session.get_api()
    db_session.global_init("vk_love_bot.db")
    longpoll = VkBotLongPoll(vk_session, 193209431)


    for event in longpoll.listen():
        # Функция позволяет группе отправлять сообщения новоприбывшему
        if event.type == VkBotEventType.GROUP_JOIN:
            user = vk.users.get(user_ids=event.obj.message['from_id'])[0]['id']
            print(f'{event.obj.user_id} вступил в группу!')
            print(f'Для того чтобы продолжить общение, '
                  f'напишите /communication. Хотите узнать мои функции - напишите /help')
            vk.messages.send(user_id=user,
                             message=f"{event.obj.message['from_id']} вступил в группу! Для того чтобы продолжить общение, "
                                     "напишите /communication. Хотите узнать мои функции - "
                                     "напишите /help", random_id=random.randint(0, 2 ** 64))

        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            user = vk.users.get(user_ids=event.obj.message['from_id'])[0]['id']
            text = event.obj.message['text']
            pprint(text)
            last_text = None # TODO ЧТО-ТО из базы
            if text == '/help':
                vk.messages.send(user_id=user,
                                 message='''Я могу познакомить вас с анонимным пользователем - /anonym_user.
                                         Но для этого заполните небольшую анкету - /questionnaire."
                                         Показать анкету случайного пользователя - /anonym_questionnaire.
                                         Понравилась анкета от анонимного пользователя - /questionnaire_anonym_user, чтобы я вас соединила в чате
                                         Также вы можете просто пообщаться со мной - /communication.
                                         Чего желаете вы?''', random_id=random.randint(0, 2 ** 64))
            elif last_text == '/questionnaire':
                # Пока особо не поняла какая должна быть анкета. Что еще добавить кроме пола и возратса?
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f"", random_id=random.randint(0, 2 ** 64))
                questionnaire = event.obj.message['text']
            elif last_text == '/set_city':
                # TODO Здесь перменная text должна записаться в таблицу
                pass
            elif last_text == '/set_age':
                # TODO Здесь перменная text должна записаться в таблицу
                pass
            elif last_text == '/set_sex':
                # Кстати можно брать данные по инфе из профиля пользователя
                # TODO Здесь перменная text должна записаться в таблицу
                pass
