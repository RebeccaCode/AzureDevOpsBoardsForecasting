import logging
import logging.config
import yaml


def get_logger(name=None):
    with open('logging_config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logger = logging.getLogger(name)

    return logger
