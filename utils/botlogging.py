import logging.config
import yaml

def init_logging():
    with open('./conf/logging.yml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
