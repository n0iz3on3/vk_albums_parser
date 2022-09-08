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
            'photo_sizes': '1'
            }
        response = requests.get(url, params={**self.params, **users_params}).json()
        return response['response']['items']
    
    def get_max_size_photos(self):
        data = self.get_data()
        max_size_photos = {(items['likes']['count'], items['date']): items['sizes'][-1]['url'] for items in data}
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
        

def record_json_file():
    data = vk.get_data()
    file_dump_list = []
    for items in data:
        file_dump_dict = {"file_name": (str(items['likes']['count'])+"-"+str(items['date'])+".jpg"), "size": items['sizes'][-1]['type']}
        file_dump_list.append(file_dump_dict)
    json_object = json.dumps(file_dump_list, indent=4)
    with open('data.json', 'w') as f:
        f.write(json_object)


if __name__ == '__main__':
    vk_token = ''
    yad_token = input("Введите токен с полигона Яндекс.Диска")
    user_id = input("Ведите id нужной страницы Вконтакте")
    album_id = 'profile' # input("Введите название альбома ('profile', 'wall', 'saved') или введите id альбома: ")
    vk = VK(vk_token, user_id)
    print(f"В альбоме {album_id} пользователя {user_id} доступно - {len(vk.get_data())} фотографий")
    # choise = int(input("Ведите количество фотографий для загрузки: "))
    def main():
        storage = int(input("Выберите хранилище: 1 - Яндекс.Диск, 2 - GoogleDrive: "))
        if storage == 1:
            uploader = YaUploader(yad_token)   
            url_photos = vk.get_max_size_photos()
            pbar = tqdm(total=len(url_photos))
            for keys, values in url_photos.items():
                path_to = "/Photos/" + str(keys)
                from_url = values
                uploader.upload_file_from_url(from_url, path_to)
                time.sleep(0.1)
                pbar.update(1)
            pbar.close()
        record_json_file()
        print("json-файл записан")
    main()