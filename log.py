import logging
from main import *

logging.basicConfig(filename='logggg.log',
                    #format='%(asctime)s %(levelname)s %(name)s %(message)s',
                    level=logging.INFO)


def log_to_file():
    logging.debug('Отправлен запрос в базу данных')
    logging.debug('Завершен запрос в базу данных')
    logging.info('Зарегестрирован новый пользователь')
    logging.warning('Что-то произошло не то')
    logging.error('Ошибка при выполнении запроса')


if __name__ == '__main__':
    log_to_file()