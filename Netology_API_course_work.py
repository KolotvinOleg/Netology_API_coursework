import requests
import json
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

TOKEN_VK = 'vk1.a.IK9rsskvSkkNIIA77Sz4O4BpvZhhpeUFwW85NPqDl9qGtlKv0sIc8JZh2dPqqDrIdqb_au00tWsTrLHyjaVM305tPkBf4T\
irmSZEnmXzqvVKFkqRhHa0VHuFqxTB0DO1mD3OTCoReR2PsjDCJvsz5sfgVHK96OEuyk_HOMtG7W-iwqNrDock2IKw245DGOxY'

#TOKEN_YANDEX = '**************'


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
        return response.json()

    def save_photos_and_json(self, id):
        photos = self.get_profile_photos(id)
        photos_dict = {}
        with alive_bar(len(photos['response']['items']), force_tty=True) as bar:
            print('Сохраняем фотографии с профиля ВК')
            for photo in photos['response']['items']:
                url_photo = photo['sizes'][-1]['url']
                photo_name = str(photo['likes']['count'])
                if f'{photo_name}.jpg' in photos_dict:
                    date = photo['date']
                    photo_name += f"_{datetime.fromtimestamp(date).strftime('%Y-%m-%d')}"
                photos_dict[f'{photo_name}.jpg'] = url_photo
                response = requests.get(url_photo)
                if 200 <= response.status_code < 300:
                    with open(f'{photo_name}.jpg', 'wb') as file:
                        file.write(response.content)
                bar()
        with open('Photos.json', 'w') as file:
            json.dump(photos_dict, file)
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

    def get_url_for_loading_file(self, file_name):
        url_for_loading_file = self.API_BASE_URL + '/v1/disk/resources/upload'
        params = {'path': f'{self.folder_name}/{file_name}'}
        response = requests.get(url_for_loading_file, params=params, headers = self.headers)
        return response.json()['href']

    def save_photos_in_folder(self, photos):
        print('Загружаем фотографии на Яндекс Диск')
        with alive_bar(len(photos), force_tty=True) as bar:
            for photo in photos:
                url_upload = self.get_url_for_loading_file(photo)
                with open(photo, 'rb') as file:
                    response = requests.put(url_upload, files = {'file': file})
                bar()

TOKEN_YANDEX = input('Введите токен с Полигона Яндекс.Диска: ')
# Сохраняем фотографии и данные о фотографиях в json-файл
id = int(input('Введите id пользователя VK, чьи фотографии вы хотите сохранить: '))
vk_client = VKAPIClient(TOKEN_VK, 91024608)
photos = vk_client.save_photos_and_json(id)

# Создаем папку на Яндекс диске
yandex_disk_client = YandexDiskAPIClient(TOKEN_YANDEX)
yandex_disk_client.creating_folder('Photos_from_VK')

#Сохраняем фотографии из профиля ВК в папку на Яндекс Диск
yandex_disk_client.save_photos_in_folder(photos)