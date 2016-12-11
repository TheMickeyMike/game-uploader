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
            url += '{}/'.format(id)
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
