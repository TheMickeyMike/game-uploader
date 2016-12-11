import getpass

import logging

from api.api_client import RobotServiceClient

from utils.config_reader import ConfigReader

# create logger
logger = logging.getLogger('game-uploader')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('game-uploader.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter_ch = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter_ch)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


print('\nReading config file...')
game_config = ConfigReader
game_config = game_config.map_config_file_to_game_obj()
print('Config file well formatted\n')
print('Please log in to finalize your uploading.')
username = input('Username: ')
password = getpass.getpass('Password:')
robot_client = RobotServiceClient(username=username, password=password)
if robot_client.username == game_config.author:
    logger.info('Author {} match username {}'.format(game_config.author, robot_client.username))
else:
    logger.info('Author {} username {} [FAIL]'.format(game_config.author, robot_client.username))
    print('Please correct author to your username')
    exit(1)
config = game_config.__dict__
robot_client.upload_game(config)