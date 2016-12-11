import json
import hashlib

import logging

from models.game import GameConfig

logger = logging.getLogger('game-uploader')

class ConfigReader(object):


    @staticmethod
    def object_decoder(obj):
        if 'config_version' in obj and obj['config_version'] == '1.0':
            system_version = obj['data']['game_requirements']['system_version']
            color_sensor = str(obj['data']['game_requirements']['sensors']['color_sensor'])
            gyro_sensor = str(obj['data']['game_requirements']['sensors']['gyro_sensor'])
            infrared_sensor = str(obj['data']['game_requirements']['sensors']['infrared_sensor'])
            ultrasonic_sensor = str(obj['data']['game_requirements']['sensors']['ultrasonic_sensor'])
            touch_sensor = str(obj['data']['game_requirements']['sensors']['touch_sensor'])
            big_motor = str(obj['data']['game_requirements']['motors']['big_motor'])
            middle_motor = str(obj['data']['game_requirements']['motors']['middle_motor'])
            string_for_hash = system_version \
                              + color_sensor \
                              + gyro_sensor \
                              + infrared_sensor \
                              + ultrasonic_sensor \
                              + touch_sensor \
                              + big_motor \
                              + middle_motor
            game_requirements_hash = hashlib.md5(string_for_hash.encode('utf-8')).hexdigest()
            logger.info("Game Requirements Hash: {}".format(game_requirements_hash))
            return GameConfig(
                name=obj['data']['name'],
                description=obj['data']['description'],
                author=obj['data']['author'],
                version=obj['data']['version'],
                robot_model=obj['data']['robot_model'],
                robot_system=obj['data']['robot_system'],
                lego_construction=obj['data']['lego_construction'],
                game_requirements=game_requirements_hash
            )
        return obj

    @staticmethod
    def map_config_file_to_game_obj():
        with open('./game_files/config.json', 'r') as f:
            read_data = f.read()
            game_obj = json.loads(read_data, object_hook=ConfigReader.object_decoder)
            logger.debug("Game object created: {}".format(game_obj.__dict__))
            return game_obj