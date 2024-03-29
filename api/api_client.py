import logging
import requests
import urllib
import json

from requests.auth import HTTPBasicAuth

from api.urls import Urls

logger = logging.getLogger('game-uploader')


class RobotServiceTokenProvider(object):
    CLIENT_ID = 'game-uploader'
    CLIENT_SECRET = '1234qwer'
    CLIENT_SCOPE = 'uploads'
    HEADERS = {
        'Content-Type': 'application/vnd.roboapp.v1+json',
        'Accept': 'application/vnd.roboapp.v1+json',
    }

    def __init__(self, username, password):
        self.username = username
        self.token = self.__get_access_token(username=username, password=password)
        self.HEADERS['Authorization'] = 'Bearer {}'.format(self.token)
        self.header_for_upload = {'Authorization': 'Bearer {}'.format(self.token)}

    def get_url(self, endpoint, id=None, filters=None):
        url = "{}/api/{}".format(Urls.BASE_URL, endpoint)
        if id:
            url += '/{}'.format(id)
        if filters:
            url += '?{}'.format(urllib.parse.urlencode(filters))
        return url

    def __get_access_token(self, username, password):
        logger.info('Getting Access token from server...')
        req = requests.post(
            self.get_url(endpoint=Urls.AUTH,
                         filters={'grant_type': 'password', 'username': username, 'password': password}),
            auth=HTTPBasicAuth(self.CLIENT_ID, self.CLIENT_SECRET),
            headers={'Accept': 'application/json'}
        )
        if req.status_code == 200:
            data = req.json()
            logger.info('Welcome {}. Your scopes: {}'.format(self.username, data['scope']))
            logger.debug('Success, token for username {} : {}'.format(self.username, data['access_token']))
            return data['access_token']
        elif req.status_code == 400:
            parsed = req.json()
            logger.warning("Can't get user token. Response status code: {} | Message: {} | Description: {}"
                           .format(req.status_code, parsed['error'], parsed['error_description']))
            exit(1)
        else:
            logger.warning(
                "Can't get user token. Response status code: {} | Message: {}".format(req.status_code, req.content))
            exit(1)


class RobotServiceClient(RobotServiceTokenProvider):
    def __init__(self, username='maciej', password='maciej'):

        super(RobotServiceClient, self).__init__(username, password)

    def upload_game(self, config):
        files = {'file': open('./game_files/game.jar', 'rb'), 'config': json.dumps(config)}
        response = requests.post(
            self.get_url(endpoint=Urls.GAMES_VAULT),
            files=files,
            headers=self.header_for_upload
        )
        if response.status_code == 200:
            data = response.json()
            logger.debug(data)
            print("Success. Your game has been uploaded.\n{}".format(json.dumps(data, indent=4, sort_keys=True)))
            return 0
        elif response.status_code == 404:
            parsed = response.json()
            logger.warning("Response status code: {} | Message: {}".format(response.status_code, parsed['userMessage']))
            exit(1)
        elif response.status_code == 400:
            parsed = response.json()
            logger.warning("Response status code: {} | Message: {}".format(response.status_code, parsed['userMessage']))
            exit(1)
        elif response.status_code == 409:
            parsed = response.json()
            logger.warning("Response status code: {} | Message: {}".format(response.status_code, parsed['userMessage']))
            exit(1)
        else:
            logger.error("Response status code: {} | Message: {}".format(response.status_code, response.content))
            exit(1)

    def contruction_helper(self,const_hash, model):
        path = '{}/{}'.format(model, const_hash)
        req = requests.get(
            self.get_url(endpoint=Urls.CONSTRUCTION_HASH, id=path),
            headers={'Accept': 'application/json'}
        )
        if req.status_code == 200:
            data = req.json()
            logger.debug('Construction for hash {} found.\n{}'.format(const_hash, json.dumps(data, indent=4, sort_keys=True)))
            print('Found construction for hash {} \nUsing construction: "{}"'.format(const_hash, data['name']))
            return data['id']
        if req.status_code == 404:
            construction_config_id = self.construction_config_fallback(const_hash)
            if not construction_config_id:
                logger.debug('Construction for hash {} not found. Trying creating one.'.format(const_hash))
                print('Construction for hash {} not found. Trying creating one.'.format(const_hash))
                req_in_json = '{req in json}'
                data = {
                    'requirements': req_in_json,
                    'config': const_hash
                }
                construction_config_id = self.create_new_construction_config(data)
            construction_name = input('Please provide name for new construction: ')
            construction_info = input('Please provide some information for this construction: ')
            new_construction = {
                'robot_model': model,
                'name': construction_name,
                'info': construction_info,
                'config': construction_config_id
            }
            new_construction_obj = self.create_new_construction(new_construction)
            return new_construction_obj['id']
        else:
            logger.error('Error while fetching construction for hash {} | Response: {}'.format(const_hash, req.json()))
            raise Exception('Error while fetching construction for hash {}'.format(const_hash))

    def create_new_construction(self, data):
        print('Creating new construction...')
        logger.debug('Trying creating new construction {}'.format(data))
        req = requests.post(
            self.get_url(endpoint=Urls.UPLOAD_CONFIG_HASH),
            headers=self.HEADERS,
            data  = json.dumps(data)
        )
        if req.status_code == 200:
            data = req.json()
            logger.debug('Construction created {}'.format(json.dumps(data, indent=4, sort_keys=True)))
            print('Construction created. ID: {}'.format(data['id']))
            logger.debug(data)
            return data
        else:
            logger.error('Error while creating new construction {} | Response: {}'.format(data, req.json()))
            raise Exception('Error while creating new construction {}'.format(data))


    def create_new_construction_config(self, data):
        print('Creating new construction configs...')
        logger.debug('Trying creating construction config {}'.format(data))
        req = requests.post(
            self.get_url(endpoint=Urls.CONSTRUCTION_HASH),
            headers=self.HEADERS,
            data=json.dumps(data)
        )
        if req.status_code == 200:
            data = req.json()
            logger.error('Construction config created {}'.format(json.dumps(data, indent=4, sort_keys=True)))
            print('Construction config created id: {}'.format(data['id']))
            return data['id']
        else:
            logger.error('Error while creating new construction config {} | Response: {}'.format(data, req.json()))
            raise Exception('Error while creating new construction config {}'.format(data))

    def construction_config_fallback(self, construction_hash):
        req = requests.get(
            self.get_url(endpoint=Urls.CONSTRUCTION_CONFIG_FALLBACK, id=construction_hash),
            headers={'Accept': 'application/json'}
        )
        if req.status_code == 200:
            data = req.json()
            logger.debug('[FALLBACK] Construction config for hash {} found.\n{}'.format(construction_hash, json.dumps(data, indent=4, sort_keys=True)))
            print('Found construction config with id {} for hash {} '.format(data['id'], construction_hash))
            return data['id']
        if req.status_code == 404:
            logger.debug('[FALLBACK] Construction config for hash {} not found.'.format(construction_hash))
            return None
        else:
            logger.error('Error while fetching construction config fallback {} | Response: {}'
                         .format(construction_hash, req.json()))
            raise Exception('Error while fetching construction config fallback {} '.format(construction_hash))