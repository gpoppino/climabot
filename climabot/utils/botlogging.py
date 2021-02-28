import logging.config
import yaml, sys, pathlib

def init_logging():
    with open(str(pathlib.Path.cwd()) + '/' + sys.argv[0] + '/climabot/conf/logging.yml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
