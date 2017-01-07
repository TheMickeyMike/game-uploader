from enum import Enum

class Urls(Enum):
    def __str__(self):
        return str(self.value)


    BASE_URL = 'http://s396393.vm.wmi.amu.edu.pl:8080'
    # BASE_URL = 'http://localhost:8080'
    AUTH = 'oauth/token'
    GAMES_VAULT = 'games/vault/upload'
    CONSTRUCTION_HASH = 'robots/config'
    UPLOAD_CONFIG_HASH = 'robots/constructions'
    CONSTRUCTION_CONFIG_FALLBACK = 'robots/lego/constructions/requirements'
