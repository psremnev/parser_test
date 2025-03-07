import requests
from fake_useragent import UserAgent


class BaseParser:
    """ Базовый парсер """

    headers = {'user-agent': UserAgent().random}

    def __init__(self):
        self.session = requests.Session()
