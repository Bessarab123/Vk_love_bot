import random
from pprint import pprint

import vk_api
import json
from data import db_session
from update_data import *
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


def send_media_file(media, user):
    if media['attachments'][0]['type'] == 'audio_message':
        id = media['attachments'][0]['audio_message']['id']
        access_key = media['attachments'][0]['audio_message']['access_key']
        vk.messages.send(user_id=user, message=media['attachments'][0]['audio_message']['link_mp3'],
                         random_id=random.randint(0, 2 ** 64))

    elif media['attachments'][0]['type'] == 'video':
        id = media['attachments'][0]['video']['id']
        attachment = f'video{user}_{id}'
        if 'access_key' in media['attachments'][0]['video'].keys():
            attachment += f"_{media['attachments'][0]['video']['access_key']}"
        vk.messages.send(user_id=user,
                         attachment=attachment,
                         random_id=random.randint(0, 2 ** 64))

    elif media['attachments'][0]['type'] == 'photo':
        id = media['attachments'][0]['photo']['id']
        attachment = f'photo{user}_{id}'
        if 'access_key' in media['attachments'][0]['photo'].keys():
            attachment += f"_{media['attachments'][0]['photo']['access_key']}"
        vk.messages.send(user_id=user,
                         attachment=attachment,
                         random_id=random.randint(0, 2 ** 64))

    elif media['attachments'][0]['type'] == 'audio':
        id = media['attachments'][0]['audio']['id']
        attachment = f'audio{user}_{id}'
        if 'access_key' in media['attachments'][0]['audio'].keys():
            attachment += f"_{media['attachments'][0]['audio']['access_key']}"
        vk.messages.send(user_id=user,
                         attachment=attachment,
                         random_id=random.randint(0, 2 ** 64))

    elif media['attachments'][0]['type'] == 'doc':
        # TODO ВЛОЖЕНИЕ УДАЛЕНО
        id = media['attachments'][0]['doc']['id']
        attachment = f'doc{user}_{id}'
        if 'access_key' in media['attachments'][0]['doc'].keys():
            attachment += f"_{media['attachments'][0]['doc']['access_key']}"
        vk.messages.send(user_id=user,
                         attachment=attachment,
                         random_id=random.randint(0, 2 ** 64))
    else:
        pprint(media)
        vk.messages.send(user_id=user,
                         message='Сорри мы пока не можем обрабатывать такие файлы',
                         random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    TEST = False
    vk_session = get_vk_session(False)
    vk = vk_session.get_api()
    db_session.global_init("vk_love_bot.db")
    longpoll = VkBotLongPoll(vk_session, 193209431)

    for event in longpoll.listen():

        # Функция позволяет группе отправлять сообщения новоприбывшему
        if event.type == VkBotEventType.GROUP_JOIN:
            pprint(event.obj)
            user_id = event.obj["user_id"]
            print(f'{event.obj.user_id} вступил в группу!')
            vk.messages.send(user_id=user_id,
                             message=f'''{user_id} вступил в группу! Для того чтобы продолжить общение,
                                        Хотите узнать мои функции - напишите /help''',
                             random_id=random.randint(0, 2 ** 64))
            # Получаем из профиля пользователя данные о нём
            data = vk.users.get(user_ids=user_id, fields='city, bdate, sex')[0]
            if data['sex'] == 1:
                sex = 'Женский'
            elif data['sex'] == 2:
                sex = 'Мужской'
            else:
                sex = 'Не указан'

            if 'city' in data.keys():
                city = data['city']['title']
            else:
                city = 'Не указан'

            if 'bdate' in data.keys():
                bdate = data['bdate']
            else:
                bdate = 'Не указан'

            update_user_data(db_session, user_id, {"sex": sex, "age": bdate, "city": city})
            print('Создание пользователя...', user_id, sex, bdate, city)

        if event.type == VkBotEventType.MESSAGE_NEW:
            user = vk.users.get(user_ids=event.obj.message['from_id'])[0]['id']
            text = event.obj.message['text']
            user_id = event.obj.message['from_id']
            last_text = get_last_message(db_session, user_id)
            update_user_data(db_session, user_id, {"last_message": text})
            if text == '/help':
                vk.messages.send(user_id=user,
                                 message='''Я могу познакомить вас анонимно с пользователем.
                                         Но для этого заполните небольшую анкету - 
                                         /set_description.
                                         Показать анкету случайного пользователя - 
                                         /anonym_questionnaire.
                                         Понравилась анкета от анонимного пользователя - 
                                         /questionnaire_anonym_user, чтобы я вас соединила в чате.
                                         Захотите прекратить общение - /stop в помощь.
                                         Также вы можете просто пообщаться со мной - /communication.
                                         Чего желаете вы?''', random_id=random.randint(0, 2 ** 64))
            elif last_text == '/set_description':
                update_user_data(db_session, user_id, {"description": text})
            elif last_text == '/set_city':
                update_user_data(db_session, user_id, {"city": text})
            elif last_text == '/set_age':
                update_user_data(db_session, user_id, {"age": text})
            elif last_text == '/set_sex':
                # Кстати можно брать данные по инфе из профиля пользователя
                update_user_data(db_session, user_id, {"sex": text})
                pass
            elif text == '/test':
                TEST = not TEST
                print(TEST)
            elif TEST:
                send_media_file(event.obj.message, user)
            elif last_text == '/communication':
                vk.messages.send(user_id=user,
                                 message='''Я совсем молодой бот, поэтому далеко не на 
                                            все смогу поговорить.''', random_id=random.randint(0, 2 ** 64))
            elif last_text == '/anonym_questionnaire':
                # TODO random_questionnaire =
                # берем рандомную анкетку из БД
                vk.message.send(user_id=user,
                                message=random_questionnaire,
                                random_id=random.randint(0, 2 ** 64))
            elif last_text == '/questionnaire_anonym_user':
                pass
                # Тут соединяются два анонимных пользователя в анонимном чате.
                # anonym_id - это чел с коорым только что начал юзер общаться.
                # Я просто не поняла как это по-нормальному сделать, поэтому будет такой корявый шаблон
                update_user_data(db_session, user_id, {'last_anonym_user_id': anonym_id})
            elif last_text == '/stop':
                scores_of_karma = 0
                vk.messages.send(user_id=user,
                                 message='''Вы соизволили прекратить общение, поставьте этому пользователю балл.
                                 Максимум - +50, минимум - -50. Ставтьте целые числа, пожалуйста.''',
                                 random_id=random.randint(0, 2 ** 64))
                if last_text[0] == '+':
                    scores_of_karma =+ int(last_text[1:])
                else:
                    scores_of_karma =- int(last_text[1:])
                update_user_data(db_session, anonym_id, {'scores': + scores_of_karma})