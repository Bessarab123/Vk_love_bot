import random
from pprint import pprint

import vk_api
import json
from data import db_session
from datetime import date
from update_data import *
from search_familiar_people import *
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


def send_text_or_file(text, user_id):
    """Обработка сообщений и последующая их отправка указонаму юзеру
    media - словарь с информацие о пришедшем сообщении
    user_id - id пользователя vk от кого надо отправить сообщение"""
    pprint(text)
    user = get_interlocutor(db_session, user_id)
    if text['attachments'] != []:
        if text['attachments'][0]['type'] == 'audio_message':
            id = text['attachments'][0]['audio_message']['id']
            access_key = text['attachments'][0]['audio_message']['access_key']
            vk.messages.send(user_id=user,
                             message=text['attachments'][0]['audio_message']['link_mp3'],
                             random_id=random.randint(0, 2 ** 64))

        elif text['attachments'][0]['type'] == 'video':
            id = text['attachments'][0]['video']['id']
            owner_id = text['attachments'][0]['video']['owner_id']
            attachment = f'video{owner_id}_{id}'
            if 'access_key' in text['attachments'][0]['video'].keys():
                attachment += f"_{text['attachments'][0]['video']['access_key']}"
            vk.messages.send(user_id=user,
                             attachment=attachment,
                             random_id=random.randint(0, 2 ** 64))

        elif text['attachments'][0]['type'] == 'photo':
            id = text['attachments'][0]['photo']['id']
            owner_id = text['attachments'][0]['photo']['owner_id']
            attachment = f'photo{owner_id}_{id}'
            if 'access_key' in text['attachments'][0]['photo'].keys():
                attachment += f"_{text['attachments'][0]['photo']['access_key']}"
            print(attachment, 'fiahosefhowweqfhoiwqhfwq')
            vk.messages.send(user_id=user,
                             attachment=attachment,
                             random_id=random.randint(0, 2 ** 64))

        elif text['attachments'][0]['type'] == 'audio':
            id = text['attachments'][0]['audio']['id']
            owner_id = text['attachments'][0]['audio']['owner_id']
            attachment = f'audio{owner_id}_{id}'
            if 'access_key' in text['attachments'][0]['audio'].keys():
                attachment += f"_{text['attachments'][0]['audio']['access_key']}"
            vk.messages.send(user_id=user,
                             attachment=attachment,
                             random_id=random.randint(0, 2 ** 64))

        elif text['attachments'][0]['type'] == 'doc':
            # TODO ВЛОЖЕНИЕ УДАЛЕНО
            id = text['attachments'][0]['doc']['id']
            owner_id = text['attachments'][0]['doc']['owner_id']
            attachment = f'doc{owner_id}_{id}'
            if 'access_key' in text['attachments'][0]['doc'].keys():
                attachment += f"_{text['attachments'][0]['doc']['access_key']}"
            vk.messages.send(user_id=user,
                             attachment=attachment,
                             random_id=random.randint(0, 2 ** 64))
        else:
            pprint(text)
            vk.messages.send(user_id=user_id,
                             message='Сорри мы пока не можем обрабатывать такие файлы',
                             random_id=random.randint(0, 2 ** 64))
    elif "text" in text:
        vk.messages.send(user_id=user, message=text["text"],
                         random_id=random.randint(0, 2 ** 64))
    else:
        print("WARRING к нам пришло что-то не то", text)


if __name__ == '__main__':
    TEST = False
    vk_session = get_vk_session(False)
    vk = vk_session.get_api()
    db_session.global_init("vk_love_bot.db")
    longpoll = VkBotLongPoll(vk_session, 193209431)
    print("Hello, world!!!")

    for event in longpoll.listen():
        if event.type == VkBotEventType.GROUP_JOIN:
            # позволяет группе отправлять сообщения новоприбывшему
            user_id = event.obj["user_id"]
            user_info = vk.users.get(user_ids=user_id)[0]
            vk.messages.send(user_id=user_id,
                             message=f'''Привет, {user_info['last_name']} {user_info['first_name']}!
                                        Вы вступили в группу! Для того чтобы продолжить общение,
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
                today = date.today()
                day, month, year = tuple(map(int, data['bdate'].split('.')))
                age = str(today.year - year - ((today.month, today.day) < (month, day)))
            else:
                age = 'Не указан'

            update_user_data(db_session, user_id, {"sex": sex, "age": age, "city": city})
            print('Создание пользователя...', user_id, sex, age, city)

        if event.type == VkBotEventType.MESSAGE_NEW:
            # Если пришло сообщение
            text = event.obj.message['text']
            print(text)
            user_id = event.obj.message['from_id']
            last_text = get_last_message(db_session, user_id)

            # Обратока сообщений условиями
            if text == '/help':
                vk.messages.send(user_id=user_id,
                                 message='''Я могу познакомить вас анонимно с пользователем.
                                         Но для этого заполните небольшую анкету - 
                                         /set_description.
                                         /set_city - поменять город
                                         /set_age - поменять возраст
                                         /set_sex - поменять пол
                                         Показать анкету случайного пользователя - 
                                         /anonymous_user.
                                         Захотите прекратить общение - /stop в помощь.
                                         Также вы можете просто пообщаться со мной - /communication.
                                         Чего желаете вы?''', random_id=random.randint(0, 2 ** 64))
            # Изменение каких то данных в бд
            elif last_text == '/set_description':
                update_user_data(db_session, user_id, {"description": text})
            elif last_text == '/set_city':
                update_user_data(db_session, user_id, {"city": text})
            elif last_text == '/set_age':
                update_user_data(db_session, user_id, {"age": text})
            elif last_text == '/set_sex':
                # Кстати можно брать данные по инфе из профиля пользователя
                update_user_data(db_session, user_id, {"sex": text})

            elif text == '/test':
                TEST = not TEST  # TODO Убрать на релизе
                print(TEST)
            elif TEST:
                pass

            elif last_text == '/communication':
                vk.messages.send(user_id=user_id,
                                 message='''Я совсем молодой бот, поэтому далеко не на 
                                            все смогу поговорить.''',
                                 random_id=random.randint(0, 2 ** 64))
            elif text == '/anonymous_user':
                # Поиск собеседников
                user_info = get_user_info(db_session, user_id)
                people = search_for_familiar_people(db_session, get_user(db_session, user_id),
                                                    user_info["age"], user_info["city"],
                                                    user_info["sex"])
                print(people, 'вот кого мы нашли')
                id_interlocutor = random.choices(people) if people else 238705165
                if id_interlocutor:

                    message = f'''Вот кого мы нашли:
                                        {get_user_info(db_session, id_interlocutor)}
                                        Если желаете начать общение то напишите Y
                                        Если хотите кого нибудь другого то N
                                        Если вам начинают попадаться те же самые люди то расширте
                                        круг поиска'''

                    update_user_data(db_session, user_id, {
                        "interlocutor": id_interlocutor})

                    vk.messages.send(user_id=user_id, message=message,
                                     random_id=random.randint(0, 2 ** 64))
                else:
                    vk.messages.send(user_id=user_id, message="Кажется мы никого не нашли "
                                                              "попытайтесь позже или расширте "
                                                              "круг поиска",
                                     random_id=random.randint(0, 2 ** 64))

            elif last_text == '/anonymous_user':
                if text == 'Y':
                    message = '''Вы подключились к собеседнику, все дальнейие сообщения будут 
                    отправлены ему, чтобы пректратить общение пропишите /stop'''
                    vk.messages.send(user_id=user_id, message=message,
                                     random_id=random.randint(0, 2 ** 64))

                    update_user_data(db_session, get_interlocutor(db_session, user_id), {
                        "interlocutor": user_id})
                    message = f'''К вам подключился пользователь! {get_user_info(db_session,
                                                                                 user_id)}
                              Вы всегда можете написать /stop и не общаться с ним'''
                    vk.messages.send(user_id=get_interlocutor(db_session, user_id), message=message,
                                     random_id=random.randint(0, 2 ** 64))
                elif text == '/stop':
                    update_user_data(db_session, user_id, {"interlocutor": None})
                else:
                    continue

            elif text == '/stop':
                vk.messages.send(user_id=user_id,
                                 message='''Вы соизволили прекратить общение, поставьте этому 
                                 пользователю балл.
                                 Максимум - +50, минимум - -50. Пишите целые числа, пожалуйста.''',
                                 random_id=random.randint(0, 2 ** 64))
                vk.messages.send(user_id=get_interlocutor(db_session, user_id),
                                 message='''С вами прекратили общение, поставьте этому 
                                                 пользователю балл.
                                                 Максимум - +50, минимум - -50. Пишите целые числа, пожалуйста.''',
                                 random_id=random.randint(0, 2 ** 64))
                update_user_data(db_session, get_interlocutor(db_session, user_id), {
                    "last_text": '/stop'})
            elif last_text == '/stop':
                if text.isdigit() and -50 <= int(text) <= 50:
                    scores_of_karma = int(text)
                    vk.messages.send(user_id=user_id, message='Спасибо за отзыв!',
                                     random_id=random.randint(0, 2 ** 64))

                else:
                    vk.messages.send(user_id=user_id, message="Вы ввели не число или оно  \nЕсли "
                                                              "не "
                                                              "хотите "
                                                              "менять рэйтин то введите - 0",
                                     random_id=random.randint(0, 2 ** 64))
                    continue
                update_user_data(db_session, get_interlocutor(db_session, user_id),
                                 {'scores': scores_of_karma})
                update_user_data(db_session, user_id, {"iinterlocutor": None})
            else:
                if get_interlocutor(db_session, user_id):
                    send_text_or_file(event.obj.message, user_id)
                else:
                    vk.messages.send(user_id=user_id, message='Разраб ленивый и не предусмотрел '
                                                              'такие слова а вот /help '
                                                              'предусмотрел',
                                     random_id=random.randint(0, 2 ** 64))

            # После всех возможных вариантов сообщений меняем last_text на text
            update_user_data(db_session, user_id, {'last_text': text})
