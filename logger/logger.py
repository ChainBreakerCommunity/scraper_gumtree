import logging

dict_level = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET
}

def get_logger(name: str, level: str, stream: bool) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(dict_level[level])
    formatter = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler("./logger/" + name + ".log")
    file_handler.setLevel(dict_level[level])
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if stream:
        stream_handler = logging.StreamHandler()
        logger.addHandler(stream_handler)
    return logger
