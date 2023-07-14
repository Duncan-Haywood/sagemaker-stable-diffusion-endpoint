import logging
from pythonjsonlogger import jsonlogger


def get_logger(name):
    """creates json logger with name=__name__ of calling file"""
    logger = logging.getLogger(name)
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    return logger
