from urllib import response
import requests
import time
from pprint import pprint
from tqdm import tqdm
import json


# with open('...', 'r') as f:
#     v_token = f.read().strip()

# with open('...', 'r') as f:
#     y_token = f.read().strip()


class VK:

    def __init__(self, vk_token, user_id, version='5.131'):
        self.token = vk_token
        self.id = user_id
        self.version = version
        self.album = album_id
        self.params = {'access_token': self.token, 'v': self.version}

    def get_users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params}).json()
        return response
    
    def get_data(self):
        url = 'https://api.vk.com/method/photos.get'
        users_params = {
            'owner_id': self.id,
            'album_id': self.album,
            'extended': '1',
            'photo_sizes': '1',
            'count': 1000
            }
        response = requests.get(url, params={**self.params, **users_params}).json()
        return response['response']['items']
    
    def get_max_size_photos(self):
        data = self.get_data()
        max_size_photos = {(str(items['likes']['count']) + "-" + str(items['date'])): items['sizes'][-1]['url'] for items in data}
        return max_size_photos


class YaUploader:

    def __init__(self, yad_token):
        self.token = yad_token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
            }

    def upload_file_from_url(self, from_url, path_to):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        payload = {
            'path': path_to, 
            'url': from_url
            }
        return requests.post(url, headers=self.get_headers(), params=payload)
    
    def create_folder(self, folder_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params = {
            'path': folder_name
        }
        folder_name = folder_name
        response = requests.put(url, headers=headers, params=params)
        status_code = response.status_code
        if status_code == 201:
            print(f"Папка {folder_name} создана")
        elif status_code == 409:
            print(f"Папка {folder_name} уже существует!")
        else:
            response.raise_for_status()


def record_json_file():
    data = vk.get_data()
    file_dump_list = []
    for items in data:
        file_dump_dict = {"file_name": (str(items['likes']['count'])+"-"+str(items['date'])+".jpg"), "size": items['sizes'][-1]['type']}
        file_dump_list.append(file_dump_dict)
    json_object = json.dumps(file_dump_list, indent=4)
    with open('data.json', 'w') as f:
        f.write(json_object)


def main():
        storage = int(input("Выберите хранилище: 1 - Яндекс.Диск, 2 - GoogleDrive: "))
        if storage == 1:
            folder_name = input("Для создания новой папки введите её название: ")
            uploader = YaUploader(yad_TOKEN)   
            uploader.create_folder(folder_name)
            url_photos = vk.get_max_size_photos()
            pbar = tqdm(total=len(url_photos))
            for keys, values in url_photos.items():
                path_to = "/" + folder_name + "/" + str(keys)
                from_url = values
                uploader.upload_file_from_url(from_url, path_to)
                time.sleep(0.1)
                pbar.update(1)
            pbar.close()
        record_json_file()
        print("json-файл записан")


if __name__ == '__main__':
    vk_TOKEN = '...'
    yad_TOKEN = input("Введите токен с полигона Яндекс.Диска: ")
    user_id = input("Ведите id нужной страницы Вконтакте: ")
    album_id = input("Введите название альбома ('profile', 'wall', 'saved') или введите id альбома: ")
    vk = VK(vk_TOKEN, user_id)
    print(f"В альбоме {album_id} пользователя {user_id} доступно - {len(vk.get_data())} фотографий")
    main()