import logging

logging.basicConfig(filename='log_file.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


# мне кажется что нет смысла в комментах, так как в логе прописываются все действия проги
def log_to_file_info_DB_send():
    logging.info('Отправлен запрос в базу данных')


def log_to_file_update_DB():
    logging.info('Обновляется база данных')


def log_to_file_info_DB_news_of_users(user_id):
    logging.info('Присоединился пользователь', user_id)


def log_to_file_stop_of_user():
    logging.info('Пользователь прекратил общение')


def log_to_file_score_distribution():
    logging.info('Пользователь ставит балл собеседнику')


def log_to_file_disclosure_of_indentity():
    logging.info('Пользователь захотел раскрыться')


def log_ban_user(id, time):
    logging.info(f"Пользователь был забанен {id} {time}")


def log_bot_wake_up():
    logging.info('Бот проснулся')


def log_to_file_error_with_DB():
    logging.warning('Какая-то беда с базой данных')


def log_to_message(text):
    logging.warning('Неизвесное сообщение: ' + str(text))


def log_critical_error(error):
    logging.critical(error)
