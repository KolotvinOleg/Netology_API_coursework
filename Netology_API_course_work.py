import requests
import json
import sys
from urllib.parse import urlencode
from datetime import datetime
from alive_progress import alive_bar

# Получаем TOKEN_VK
base_url = 'https://oauth.vk.com/authorize'
client_id = '51750439'
params = {
    'client_id': client_id,
    'redirect_uri': 'https://oauth.vk.com/blank.html',
    'display': 'page',
    'scope': 'photos',
    'response_type': 'token'
}

oauth_url = f'{base_url}?{urlencode(params)}'
# print(oauth_url)

TOKEN_VK = '****************'


class VKAPIClient:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }

    def get_profile_photos(self, id):
        params = self.get_common_params()
        params.update({'owner_id': id, 'album_id': 'profile', 'extended': 1})
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        for key in response.json():
            if key == 'error':
                sys.exit(1)
        return response.json()

    def save_info_about_photos(self, id):
        photos = self.get_profile_photos(id)
        photos_dict = {}
        for photo in photos['response']['items']:
            url_photo = photo['sizes'][-1]['url']
            photo_name = str(photo['likes']['count'])
            size_photo = photo['sizes'][-1]['type']
            if f'{photo_name}.jpg' in photos_dict:
                date = photo['date']
                photo_name += f"_{datetime.fromtimestamp(date).strftime('%Y-%m-%d')}"
            photos_dict[f'{photo_name}.jpg'] = [url_photo, size_photo]
        return photos_dict


class YandexDiskAPIClient:
    API_BASE_URL = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        self.headers = {'Authorization': token}

    def creating_folder(self, folder_name):
        self.folder_name = folder_name
        url_for_creating_folder = self.API_BASE_URL + '/v1/disk/resources'
        params = {'path': self.folder_name}
        response = requests.put(url_for_creating_folder, params=params, headers=self.headers)

    def save_photos_in_folder(self, photos, folder_name):
        self.creating_folder(folder_name)
        url_for_loading_file = self.API_BASE_URL + '/v1/disk/resources/upload'
        print('Загружаем фотографии на Яндекс Диск')
        with alive_bar(len(photos), force_tty=True) as bar:
            photos_lst = []
            for key, value in photos.items():
                json_dict = {'file_name': key, 'size': value[1]}
                photos_lst.append(json_dict)
                params = {'path': f'{folder_name}/{key}', 'url': value[0]}
                response = requests.post(url_for_loading_file, params=params, headers=self.headers)
                bar()
        with open('Photos_info.json', 'w') as file:
            json.dump(photos_lst, file)


# Сохраняем информацию о фотографиях с профиля ВК
id = int(input('Введите id пользователя VK, чьи фотографии мы хотим сохранить: '))
vk_client = VKAPIClient(TOKEN_VK, 91024608)
photos = vk_client.save_info_about_photos(id)

# Сохраняем фотографии из профиля ВК в папку на Яндекс Диск
TOKEN_YANDEX = input('Введите токен с Полигона Яндекс.Диска: ')
yandex_disk_client = YandexDiskAPIClient(TOKEN_YANDEX)
yandex_disk_client.save_photos_in_folder(photos, 'Photos_from_VK')