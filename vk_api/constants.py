import requests
import time
from config import api_key


class VkApi:
    API_VERSION_VK = '5.103'
    URL_VK = 'https://api.vk.com/method/'
    TOKEN = api_key
    PARAMS = {}

    def __init__(self):
        self.PARAMS = {
            'access_token': self.TOKEN,
            'v': self.API_VERSION_VK
        }

    def get_response(self, method, params=None):
        if params is None:
            current_params = self.PARAMS
        else:
            current_params = self.PARAMS
            current_params.update(params)
        cur_url = self.URL_VK + method
        response = requests.get(cur_url, current_params)
        time.sleep(0.4)
        json_ = response.json()
        return json_
