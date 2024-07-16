import logging

class RelativeSeconds(logging.Formatter):
    def format(self, record):
        record.relativeCreated = record.relativeCreated // 1000
        return super().format(record)

class Logger:
    @staticmethod
    def initialize(verbose: bool):
        formatter = RelativeSeconds("%(relativeCreated)ds - %(levelname).1s: %(message)s")
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format="",
        )
        logging.root.handlers[0].setFormatter(formatter)

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
