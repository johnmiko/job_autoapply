import logging

from autoapply.linkedin.constants import GLOBAL_LOG_LEVEL


def create_logger(name):
    logging.basicConfig(filename='log_file.txt',
                        filemode='a',
                        format='%(asctime)s, %(message)s',
                        datefmt='%Y-%M-%d %H:%M:%S',
                        level=logging.INFO)

    level = GLOBAL_LOG_LEVEL
    logger = logging.getLogger(name)
    logger.setLevel(level)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(level)
    logger.addHandler(c_handler)
    return logger, c_handler
