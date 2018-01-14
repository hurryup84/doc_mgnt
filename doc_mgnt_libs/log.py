import logging
import os

def setup_custom_logger(name, filename, level, logtype="a"):
    formatter = logging.Formatter(fmt='%(asctime)s - [%(levelname)-7s] - [%(module)-10s] - %(message)s')

    fhandler = logging.FileHandler(filename, logtype)
    fhandler.setFormatter(formatter)

    logger = logging.getLogger(name)
    if level == "INFO":
    	logger.setLevel(logging.INFO)
    elif level == "DEBUG":
    	logger.setLevel(logging.DEBUG)
    else:
    	logger.setLevel(logging.DEBUG)
    logger.addHandler(fhandler)


    shandler = logging.StreamHandler()
    shandler.setFormatter(formatter)

    logger.addHandler(shandler)

    return logger


