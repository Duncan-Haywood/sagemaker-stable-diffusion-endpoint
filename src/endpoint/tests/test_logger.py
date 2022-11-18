from endpoint import logger


def test_get_logger():
    name = "main"
    logger.get_logger(name)
