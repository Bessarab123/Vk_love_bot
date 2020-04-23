import logging
from main import *

logging.basicConfig(filename='logggg.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

# мне кажется что нет смысла в комментах, так как в логе прописываются все действия проги
def log_to_file_info_DB_send():
    logging.info('Отправлен запрос в базу данных')


def log_to_file_update_DB():
    logging.info('Обновляется база данных')


def log_to_file_info_DB_news_of_users():
    logging.info('Зарегестрирован новый пользователь')


def log_to_file_messegas_of_users():
    logging.info('Пользователь что то пишет нам')


def log_to_file_stop_of_user():
    logging.info('Пользователь прекратил общение')


def log_to_file_score_distribution():
    logging.info('Пользователь ставит балл собеседнику')


def log_to_file_disclosure_of_indentity():
    logging.info('Пользователь захотел раскрыться')


def log_to_file_karma():
    logging.info('У нас ругаться нельзя. Госпожа Карма любит вежливых людей. За гадости в сообщениях снижает рейтинг')
    f = open('Для_цензуры_не_смотреть.txt', mode='r')
    censorship = f.split()
    for i in censorship:
        if i in last_text:
            scores -= 1


def log_to_file_error_with_DB():
    logging.warning('Какая-то беда с базой данных')