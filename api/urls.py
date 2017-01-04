from enum import Enum

class Urls(Enum):
    def __str__(self):
        return str(self.value)


    BASE_URL = 'http://s396393.vm.wmi.amu.edu.pl:8080'
    AUTH = 'oauth/token'
    GAMES_VAULT = 'games/vault/upload'
