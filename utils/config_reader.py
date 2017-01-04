import json
import hashlib

import logging

import sys

from models.game import GameConfig

logger = logging.getLogger('game-uploader')


class ConfigTranslator_1_0:
    def __init__(self, obj):
        self.system_version = obj['data']['game_requirements']['system_version']
        self.sensor_port_1 = self.validate_sensor(obj['data']['game_requirements']['sensor_ports']['1'])
        self.sensor_port_2 = self.validate_sensor(obj['data']['game_requirements']['sensor_ports']['2'])
        self.sensor_port_3 = self.validate_sensor(obj['data']['game_requirements']['sensor_ports']['3'])
        self.sensor_port_4 = self.validate_sensor(obj['data']['game_requirements']['sensor_ports']['4'])
        self.motor_port_1 = self.validate_motor(obj['data']['game_requirements']['motor_ports']['A'])
        self.motor_port_2 = self.validate_motor(obj['data']['game_requirements']['motor_ports']['B'])
        self.motor_port_3 = self.validate_motor(obj['data']['game_requirements']['motor_ports']['C'])
        self.string_for_hash = self.string_for_hash = self.system_version + self.sensor_port_1 + self.sensor_port_2 + \
                                                      self.sensor_port_3 + self.sensor_port_4 + self.motor_port_1 + \
                                                      self.motor_port_2 + self.motor_port_3

    def validate_sensor(self, value):
        valid_sensors = ['color_sensor', 'gyro_sensor', 'infrared_sensor', 'ultrasonic_sensor', 'touch_sensor']
        if value in valid_sensors:
            return value
        else:
            raise Exception('Valid value for this field {}, your value: {}'.format(valid_sensors, value))

    def validate_motor(self, value):
        valid_motors = ['big_motor', 'middle_motor']
        if value in valid_motors:
            return value
        else:
            raise Exception('Valid value for this field {}, your value: {}'.format(valid_motors, value))

    def get_hash(self):
        raise NotImplementedError()


class ConfigTranslatorNXT_1_0(ConfigTranslator_1_0):
    def __init__(self, obj):
        super().__init__(obj)

    def get_hash(self):
        game_requirements_hash = hashlib.md5(self.string_for_hash.encode('utf-8')).hexdigest()
        logger.info("Game Requirements Hash: {}".format(game_requirements_hash))
        return game_requirements_hash


class ConfigTranslatorEV3_1_0(ConfigTranslator_1_0):
    def __init__(self, obj):
        super().__init__(obj)
        self.motor_port_4 = self.validate_motor(obj['data']['game_requirements']['motor_ports']['D'])

    def get_hash(self):
        self.string_for_hash = self.string_for_hash + self.motor_port_4
        game_requirements_hash = hashlib.md5(self.string_for_hash.encode('utf-8')).hexdigest()
        logger.info("Game Requirements Hash: {}".format(game_requirements_hash))
        return game_requirements_hash


class ConfigReader:
    @staticmethod
    def object_decoder(json_obj):
        translator = None
        if json_obj['config_version'] == '1.0':
            if json_obj['data']['robot_model'] == 'NXT':
                translator = ConfigTranslatorNXT_1_0(obj=json_obj)
            elif json_obj['data']['robot_model'] == 'EV3':
                translator = ConfigTranslatorEV3_1_0(obj=json_obj)
            else:
                raise Exception('Model not supported')
        else:
            raise Exception('This config_version is not supported')

        return GameConfig(
            name=json_obj['data']['name'],
            description=json_obj['data']['description'],
            author=json_obj['data']['author'],
            version=json_obj['data']['version'],
            robot_model=json_obj['data']['robot_model'],
            robot_system=json_obj['data']['robot_system'],
            lego_construction=json_obj['data']['lego_construction'],
            game_requirements=translator.get_hash()
        )

    @staticmethod
    def map_config_file_to_game_obj():
        try:
            json_data = json.loads(open('./game_files/config.json').read())
            game_obj = ConfigReader.object_decoder(json_obj=json_data)
            logger.debug("Game object created: {}".format(game_obj.__dict__))
            return game_obj
        except Exception as e:
            logger.exception(e)
            sys.exit(3)
