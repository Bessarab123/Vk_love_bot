# - *- coding: utf- 8 - *-
import datetime
import random
import time
from pprint import pprint
import vk_api
import json
from data import db_session
from update_data import *
from search_familiar_people import search_for_familiar_people
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType



def get_vk_session():
    # Взять session группы
    with open("pass.json") as f:
        data = json.load(f)
        api = data["api"]
    vk_session = vk_api.VkApi(token=api)
    return vk_session


def send_text_or_file(text, user_id):
    """Обработка сообщений и последующая их отправка указонаму юзеру
    media - словарь с информацие о пришедшем сообщении
    user_id - id пользователя vk от кого надо отправить сообщение"""
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
    TEST = False  # Переменная для тестов
    vk_session = get_vk_session()  # Создаём сессию
    vk = vk_session.get_api()
    db_session.global_init("vk_love_bot.db")
    longpoll = VkBotLongPoll(vk_session, 193209431)
    print("Hello, world!!!")

    for event in longpoll.listen():
        if event.type == VkBotEventType.GROUP_JOIN:
            # позволяет группе отправлять сообщения новоприбывшему
            user_id = event.obj["user_id"]
            create_data_user(db_session, user_id, vk)
            user_info = vk.users.get(user_ids=user_id)[0]
            vk.messages.send(user_id=user_id,
                             message=f"Привет, {user_info['last_name']} {user_info['first_name']}!\n"
                                     "Вы вступили в группу! Для того чтобы продолжить общение,"
                                     "Хотите узнать мои функции - напишите /help",
                             random_id=random.randint(0, 2 ** 64))

        if event.type == VkBotEventType.MESSAGE_NEW:
            # Если пришло сообщение
            text = event.obj.message['text']
            print(text)
            user_id = event.obj.message['from_id']
            last_text = get_last_message(db_session, user_id)

            # Обратока сообщений условиями
            if text == '/help':
                vk.messages.send(user_id=user_id,
                                 message="Я могу познакомить вас анонимно с пользователем.\n"
                                         "/set_description - Заполнить анкету\n"
                                         "/set_city - поменять город\n"
                                         "/set_age - поменять возраст\n"
                                         "/set_sex - поменять пол\n"
                                         "/anonymous_user age:17,city:Тула,sex:1, - познакомиться с кем-нибудь\n"
                                         "age, city, sex - необезательные переменные для уточнения поиска\n"
                                         "при их отсутвии бот посторается найти наилучшего собеседника\n"
                                         "Захотите прекратить общение - /stop в помощь.\n"
                                         "Также вы можете просто пообщаться со мной - /communication.\n"
                                         "Если у вас есть предложения то пишите на почту bessarab.2003@yandex.ru\n"
                                         "Чего желаете вы?",
                                 random_id=random.randint(0, 2 ** 64))
            # Изменение каких то данных в бд
            elif last_text == '/set_description':
                update_user_data(db_session, user_id, {"description": text})
            elif last_text == '/set_city':
                update_user_data(db_session, user_id, {"city": text})
            elif last_text == '/set_age':
                update_user_data(db_session, user_id, {"age": text})
            elif last_text == '/set_sex':
                update_user_data(db_session, user_id, {"sex": text})

            elif text == '/test':
                TEST = not TEST  # TODO Убрать на релизе
                print(TEST)

            elif last_text == '/communication':
                vk.messages.send(user_id=user_id,
                                 message='''Я совсем молодой бот, поэтому далеко не на 
                                            все смогу поговорить.''',
                                 random_id=random.randint(0, 2 ** 64))
            elif '/anonymous_user' in text:
                # Поиск собеседников
                user_info = get_user_info(db_session, user_id)
                people = search_for_familiar_people(db_session, get_user(db_session, user_id),
                                                    user_info["age"], user_info["city"],
                                                    user_info["sex"])
                print(people, 'вот кого мы нашли')
                id_interlocutor = random.choices(people) if people else 238705165
                if id_interlocutor:
                    # Если был подобран собеседник
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
                # Предлагаем пользователю согласиться связаться с пользователем
                if text == 'Y':
                    message = '''Вы подключились к собеседнику, все дальнейие сообщения будут 
                    отправлены ему, чтобы пректратить общение пропишите /stop_search'''
                    vk.messages.send(user_id=user_id, message=message,
                                     random_id=random.randint(0, 2 ** 64))

                    update_user_data(db_session, get_interlocutor(db_session, user_id), {
                        "interlocutor": user_id})
                    message = f'''К вам подключился пользователь! {get_user_info(db_session,
                                                                                 user_id)}\n
                              Вы всегда можете написать /stop_search и не общаться с ним'''
                    vk.messages.send(user_id=get_interlocutor(db_session, user_id),
                                     message=message,
                                     random_id=random.randint(0, 2 ** 64))
                elif text == '/stop_search':
                    update_user_data(db_session, user_id, {"interlocutor": None})
                else:
                    continue

            elif text == '/stop':
                # Если при общении пользователь пишет /stop то просим его ввести число
                vk.messages.send(user_id=user_id,
                                 message="Вы соизволили прекратить общение, поставьте этому"
                                         "пользователю балл.\n"
                                         "Максимум +50, минимум -50."
                                         " Пишите целые числа, пожалуйста.",
                                 random_id=random.randint(0, 2 ** 64))
                vk.messages.send(user_id=get_interlocutor(db_session, user_id),
                                 message="С вами прекратили общение, поставьте этому "
                                         "пользователю балл.\n"
                                         "Максимум +50, минимум -50. "
                                         "Пишите целые числа, пожалуйста.",
                                 random_id=random.randint(0, 2 ** 64))
                update_user_data(db_session, get_interlocutor(db_session, user_id), {
                    "last_text": '/stop'})
            elif last_text == '/stop':
                # Если пользователь попросил остановиться то ожидаем от него числа
                if text.isdigit() and -50 <= int(text) <= 50:
                    scores_of_karma = int(text)
                    vk.messages.send(user_id=user_id, message='Спасибо за отзыв!',
                                     random_id=random.randint(0, 2 ** 64))

                else:
                    vk.messages.send(user_id=user_id, message="Вы ввели не число или оно не "
                                                              "соответсыует указаниям"
                                                              "\nЕсли не хотите менять "
                                                              "рэйтин то введите - 0",
                                     random_id=random.randint(0, 2 ** 64))
                    continue
                update_user_data(db_session, get_interlocutor(db_session, user_id),
                                 {'scores': scores_of_karma})
                update_user_data(db_session, user_id, {"interlocutor": None})
            else:
                # Если это не команда то смотрим общается ли пользоваетль с кем-то
                if get_interlocutor(db_session, user_id):
                    # Если пользователь общается с кем-то
                    send_text_or_file(event.obj.message, user_id)
                else:
                    # Если пользователь надеется поговорить с нами
                    vk.messages.send(user_id=user_id, message='Разраб ленивый и не предусмотрел '
                                                              'такие слова а вот /help '
                                                              'предусмотрел',
                                     random_id=random.randint(0, 2 ** 64))

            # После всех возможных вариантов сообщений меняем last_text на text
            update_user_data(db_session, user_id, {'last_text': text})
        if datetime.datetime.now().strftime("%H:%M:%S") == "00:00:30" or TEST:
            # Обновление базы данных
            update_db(db_session, vk)
            time.sleep(1)
            TEST = False
