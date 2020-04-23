import logging
from main import *

logging.basicConfig(filename='logggg.log',
                    #format='%(asctime)s %(levelname)s %(name)s %(message)s',
                    level=logging.INFO)


def log_to_file():
    logging.info('Вот что делает программа')


if __name__ == '__main__':
    log_to_file()