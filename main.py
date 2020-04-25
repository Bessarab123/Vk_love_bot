# - *- coding: utf- 8 - *-
import json
import random
from pprint import pprint

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime
from data import db_session
from log import *
from search_familiar_people import search_for_familiar_people
from update_data import *


def get_vk_session():
    # Взять session группы
    with open("pass.json") as f:
        data = json.load(f)
        api = data["api"]
    vk_session = vk_api.VkApi(token=api)
    return vk_session


def send_text_or_file(text, user_id, vk):
    pprint(text)
    """Обработка сообщений и последующая их отправка указонаму юзеру
    media - словарь с информацие о пришедшем сообщении
    user_id - id пользователя vk от кого надо отправить сообщение"""
    user = get_interlocutor(db_session, user_id)
    if text['attachments']:
        if text['attachments'][0]['type'] == 'video':
            id_media = text['attachments'][0]['video']['id']
            owner_id = text['attachments'][0]['video']['owner_id']
            attachment = f'video{owner_id}_{id_media}'
            if 'access_key' in text['attachments'][0]['video'].keys():
                attachment += f"_{text['attachments'][0]['video']['access_key']}"
            vk.messages.send(user_id=user,
                             attachment=attachment,
                             random_id=random.randint(0, 2 ** 64))


        elif text['attachments'][0]['type'] == 'audio':
            id_media = text['attachments'][0]['audio']['id']
            owner_id = text['attachments'][0]['audio']['owner_id']
            attachment = f'audio{owner_id}_{id_media}'
            if 'access_key' in text['attachments'][0]['audio'].keys():
                attachment += f"_{text['attachments'][0]['audio']['access_key']}"
            log_to_file_info_DB_send()
            vk.messages.send(user_id=user,
                             attachment=attachment,
                             random_id=random.randint(0, 2 ** 64))
        else:
            log_to_file_info_DB_send()
            vk.messages.send(user_id=user_id,
                             message='Сорри, я пока не могу обрабатывать такие файлы',
                             random_id=random.randint(0, 2 ** 64))
    elif "text" in text:
        log_to_file_info_DB_send()
        vk.messages.send(user_id=user, message=text["text"],
                         random_id=random.randint(0, 2 ** 64))
    else:
        log_to_message(text)


def main():
    TEST = False
    bad_words = set(get_data_from_file())
    vk_session = get_vk_session()  # Создаём сессию
    vk = vk_session.get_api()
    db_session.global_init("vk_love_bot.db")
    longpoll = VkBotLongPoll(vk_session, 193209431)
    log_bot_wake_up()
    for event in longpoll.listen():
        if event.type == VkBotEventType.GROUP_JOIN:
            # пишет в лог про новоприбывшего
            # позволяет группе отправлять сообщения новоприбывшему
            user_id = event.obj["user_id"]
            log_to_file_info_DB_news_of_users(user_id)
            create_data_user(db_session, user_id, vk, True)
            user_info = vk.users.get(user_ids=user_id)[0]
            vk.messages.send(user_id=user_id,
                             message="Привет,"
                                     f" {user_info['last_name']} {user_info['first_name']}!\n"
                                     "Вы вступили в группу!\n"
                                     "Я Бот для анонимных знакомств и общения\n"
                                     "Хотите подробние узнать мои функции - напишите /help\n"
                                     "Для вашего блага "
                                     "- пишите цензурно, без мата.",
                             random_id=random.randint(0, 2 ** 64))
        elif event.type == VkBotEventType.GROUP_LEAVE:
            user_id = event.obj["user_id"]
            update_user_data(db_session, user_id, {"in_group": False})
        elif event.type == VkBotEventType.MESSAGE_NEW:
            # Если пришло сообщение
            text = event.obj.message['text']
            user_id = event.obj.message['from_id']
            log_to_file_info_DB_send()
            last_text = get_last_message(db_session, user_id)
            # Обратока сообщений условиями
            if text == '/help':
                log_to_file_info_DB_send()
                vk.messages.send(user_id=user_id,
                                 message="Я могу познакомить вас анонимно с пользователем.\n"
                                         "/set_description - заполнить анкету - ключевой параметр"
                                         " о вас расскажите о себе здесь и это будут видеть "
                                         "другие пользователи\n"
                                         "/set_city - указать или поменять город\n"
                                         "/set_age - указать или поменять возраст\n"
                                         "/set_sex - указать или поменять пол\n"
                                         "/anonymous_user sex=Ж, age=21, city=Москва, rout=1 - "
                                         "познакомиться с кем-нибудь\n"
                                         "sex, age, city, rout - необязательные параметры. "
                                         "Указывать строго как в примере"
                                         "rout - глубина поиска\n1 - самые подходящие\n"
                                         "2 - не учитывается город\n3 - не учитывается пол\n4 - "
                                         "не учитывается возраст"
                                         "Бот будет показывать чужие анкеты, а Вы выбирать с кем "
                                         "желаете пообщаться\n"
                                         "/show_scores - показать ваши очки, если они будут ниже "
                                         "-500 то вы будете забанены на расчитанный срок\n"
                                         "/get_info - бот покажет вашу информацию вам "
                                         "Захотите прекратить общение - /stop в помощь.\n"
                                         "Хотите открыть свою страницу собеседнику - /show_me.\n"
                                         "Если вы не хотите чтобы ваша анкета показывалась "
                                         "пользователям то достаточно просто выйти из группы\n"
                                         "Также вы можете просто пообщаться со мной - "
                                         "/communication.\n"
                                         "Если у вас есть предложения, то пишите на почту "
                                         "bessarab.2003@yandex.ru\n"
                                         "nastya.nedoseicko@yandex.ru\n"
                                         "Svetlana.telnova@icloud.com\n"
                                         "Чего желаете, вы?",
                                 random_id=random.randint(0, 2 ** 64))
            # Изменение каких то данных в бд
            elif last_text == '/set_description':
                log_to_file_info_DB_send()
                update_user_data(db_session, user_id, {"description": text})
            elif last_text == '/set_city':
                log_to_file_info_DB_send()
                update_user_data(db_session, user_id, {"city": text})
            elif last_text == '/set_age':
                if text.isdigit() and int(text) > 0:
                    log_to_file_info_DB_send()
                    update_user_data(db_session, user_id, {"age": text})
                    vk.messages.send(user_id=user_id, message="Успешно изменено",
                                     random_id=random.randint(0, 2 ** 64))
                else:
                    vk.messages.send(user_id=user_id, message="Неверно указан возраст",
                                     random_id=random.randint(0, 2 ** 64))
            elif last_text == '/set_sex':
                if text in ('M', 'Ж'):
                    log_to_file_info_DB_send()
                    update_user_data(db_session, user_id, {"sex": text})
                    vk.messages.send(user_id=user_id, message="Успешно изменено",
                                     random_id=random.randint(0, 2 ** 64))
                else:
                    vk.messages.send(user_id=user_id, message="Неверно указан пол",
                                     random_id=random.randint(0, 2 ** 64))
            elif text == '/set_description':
                vk.messsages.send(user_id=user_id, message='Введите описание:',
                                  random_id=random.randint(0, 2 ** 64))
            elif text == '/set_city':
                vk.messsages.send(user_id=user_id, message='Введите город:',
                                  random_id=random.randint(0, 2 ** 64))
            elif text == '/set_age':
                vk.messsages.send(user_id=user_id, message='Введите возраст:',
                                  random_id=random.randint(0, 2 ** 64))
            elif text == '/set_sex':
                vk.messsages.send(user_id=user_id, message='Введите пол М/Ж:',
                                  random_id=random.randint(0, 2 ** 64))
            elif text == '/show_scores':
                vk.messages.send(user_id=user_id,
                                 message=f"Ваши очки: {get_score(db_session, user_id)}",
                                 random_id=random.randint(0, 2 ** 64))
            elif text == '/test':
                TEST = not TEST
            elif "/get_info" == text:
                vk.messages.send(user_id=user_id,
                                 message=f"Ваши информация: {get_user_info(db_session, user_id)}",
                                 random_id=random.randint(0, 2 ** 64))
            elif last_text == '/communication':
                log_to_file_info_DB_send()
                vk.messages.send(user_id=user_id,
                                 message='''Я совсем молодой бот, поэтому далеко не на 
                                            все смогу поговорить. Могу морально поддержать.''',
                                 random_id=random.randint(0, 2 ** 64))
                if ('плохо' in text or 'ужасно' in text or 'отвратительно' in text
                        or 'мерзко' in text):
                    log_to_file_info_DB_send()
                    vk.messages.send(user_id=user_id,
                                     message="Не расстраивайтесь! Когда вы считаете, что все очень"
                                             " плохо, то потом"
                                             "будет просто замечательно.",
                                     random_id=random.randint(0, 2 ** 64))
            elif '/anonymous_user' in text:
                info = text.split()
                sex, age, city = [None] * 3
                rout = 1
                # Проработка дополнительных параметров
                try:
                    for i in info:
                        if 'sex' in i:
                            sex = i.split('=')[1]
                            if not (sex in ['М', 'Ж']):
                                raise InputInfoUserError
                        elif 'city' in i:
                            city = i.split('=')[1]
                        elif 'age' in i:
                            age = i.split('=')[1]
                            if not age.isdigit() or int(age) < 1:
                                raise InputInfoUserError
                            age = int(age)
                        elif 'rout' in i:
                            rout = i.split('=')[1]
                            if not rout.isdigit() or int(rout) < 1 or int(rout) > 5:
                                raise InputInfoUserError
                            rout = int(rout)
                except InputInfoUserError or IndexError:
                    vk.messages.send(user_id=user_id, message="Неверные параметры поиска",
                                     random_id=random.randint(0, 2 ** 64))
                # Поиск собеседников
                log_to_file_info_DB_send()
                people, rout = search_for_familiar_people(db_session,
                                                          get_user(db_session, user_id),
                                                          sex_interlocutor=sex,
                                                          city_interlocutor=city,
                                                          age_interlocutor=age,
                                                          rout=rout)
                if people:
                    id_interlocutor = random.choice(people)
                    # Если был подобран собеседник
                    log_to_file_info_DB_send()
                    message = f'''Вот кого мы нашли на {rout} проходе:
                                  {get_user_info(db_session, id_interlocutor)}
                                  Если желаете начать общение, то напишите Y
                                  Если хотите кого нибудь другого, то N
                                  Если вам начинают попадаться те же самые люди то лучше 
                                  подождите. Если хотите остновить поиск - /stop_search'''
                    log_to_file_info_DB_send()
                    update_user_data(db_session, user_id, {
                        "interlocutor": id_interlocutor})
                    log_to_file_info_DB_send()
                    vk.messages.send(user_id=user_id, message=message,
                                     random_id=random.randint(0, 2 ** 64))
                else:
                    log_to_file_info_DB_send()
                    vk.messages.send(user_id=user_id, message="Кажется, мы никого не нашли "
                                                              "попытайтесь позже или расширьте "
                                                              "круг поиска",
                                     random_id=random.randint(0, 2 ** 64))

            elif last_text == '/anonymous_user':
                # Предлагаем пользователю согласиться связаться с пользователем
                if text == 'Y':
                    message = '''Вы подключились к собеседнику, все дальнейшие сообщения будут 
                    отправлены ему, чтобы пректратить общение пропишите /stop'''
                    log_to_file_info_DB_send()
                    vk.messages.send(user_id=user_id, message=message,
                                     random_id=random.randint(0, 2 ** 64))
                    log_to_file_info_DB_send()
                    update_user_data(db_session, get_interlocutor(db_session, user_id), {
                        "interlocutor": user_id})
                    log_to_file_info_DB_send()
                    message = f'''К вам подключился пользователь! {get_user_info(db_session,
                                                                                 user_id)}\n
                              Вы всегда можете написать /stop и не общаться с ним'''
                    log_to_file_info_DB_send()
                    vk.messages.send(user_id=get_interlocutor(db_session, user_id),
                                     message=message,
                                     random_id=random.randint(0, 2 ** 64))
                elif text == '/stop_search':
                    log_to_file_info_DB_send()
                    update_user_data(db_session, user_id, {"interlocutor": None})
                else:
                    continue

            elif last_text == '/show_me':
                log_to_file_disclosure_of_indentity()
                log_to_file_info_DB_send()
                vk.message.send(user_id=get_interlocutor(db_session, user_id),
                                message=f'Собеседник захотел открыться вам. Вот его ID - {user_id}',
                                random_id=random.randint(0, 2 ** 64))

            elif text == '/stop':
                log_to_file_stop_of_user()
                # Если при общении пользователь пишет /stop то просим его ввести число
                log_to_file_info_DB_send()
                vk.messages.send(user_id=user_id,
                                 message="Вы соизволили прекратить общение, поставьте этому"
                                         "пользователю балл.\n"
                                         "Максимум +50, минимум -50."
                                         " Пишите целые числа, пожалуйста.",
                                 random_id=random.randint(0, 2 ** 64))
                log_to_file_info_DB_send()
                vk.messages.send(user_id=get_interlocutor(db_session, user_id),
                                 message="С вами прекратили общение, поставьте этому "
                                         "пользователю балл.\n"
                                         "Максимум +50, минимум -50. "
                                         "Пишите целые числа, пожалуйста.",
                                 random_id=random.randint(0, 2 ** 64))
                log_to_file_info_DB_send()
                update_user_data(db_session, get_interlocutor(db_session, user_id), {
                    "last_text": '/stop'})
            elif last_text == '/stop':
                # Если пользователь попросил остановиться то ожидаем от него числа
                log_to_file_score_distribution()
                if text.isdigit() and -50 <= int(text) <= 50:
                    scores_of_karma = int(text)
                    log_to_file_info_DB_send()
                    vk.messages.send(user_id=user_id, message='Спасибо за отзыв!',
                                     random_id=random.randint(0, 2 ** 64))

                else:
                    log_to_file_info_DB_send()
                    vk.messages.send(user_id=user_id, message="Вы ввели не число или оно не "
                                                              "соответсвует указаниям"
                                                              "\nЕсли не хотите менять "
                                                              "рэйтинг, то введите - 0",
                                     random_id=random.randint(0, 2 ** 64))
                    continue
                log_to_file_info_DB_send()
                update_user_data(db_session, get_interlocutor(db_session, user_id),
                                 {'scores': scores_of_karma})
                update_user_data(db_session, user_id, {"interlocutor": None})
            else:
                # Если это не команда то смотрим общается ли пользоваетль с кем-то
                log_to_file_info_DB_send()
                # Проверка на некультурность
                scores = 0
                for word in bad_words:
                    if word in text.lower():
                        scores += 5
                update_user_data(db_session, user_id, {"scores": -scores})
                if get_interlocutor(db_session, user_id):
                    # Если пользователь общается с кем-то
                    log_to_file_info_DB_send()
                    send_text_or_file(event.obj.message, user_id, vk)
                else:
                    # Если пользователь надеется поговорить с нами
                    log_to_file_info_DB_send()
                    vk.messages.send(user_id=user_id, message='Разраб ленивый и не предусмотрел '
                                                              'такие слова а вот /help '
                                                              'предусмотрел',
                                     random_id=random.randint(0, 2 ** 64))

            # После всех возможных вариантов сообщений меняем last_text на text
            log_to_file_info_DB_send()
            update_user_data(db_session, user_id, {'last_text': text})
        if datetime.datetime.now().strftime("%H:%M:%S") == "00:00:30" or TEST:
            TEST = False
            # Обновление базы данных
            log_to_file_update_DB()
            update_db(db_session, vk)


def get_data_from_file():
    with open("Bad_words.txt", mode='r') as file:
        return file.read().split(', ')


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            log_critical_error(e)
