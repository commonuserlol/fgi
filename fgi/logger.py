import logging

class Logger:
    @staticmethod
    def debug(msg: str):
        logging.debug(msg)

    @staticmethod
    def info(msg: str):
        logging.info(msg)

    @staticmethod
    def warn(msg: str):
        logging.warning(msg)

    @staticmethod
    def error(msg: str):
        logging.error(msg)
