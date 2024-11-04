import os
import requests
import json
from tqdm import tqdm
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# Загрузка токенов из config.env
load_dotenv("config.env")
VK_TOKEN = os.getenv('VK_TOKEN')
YA_TOKEN = os.getenv('YA_TOKEN')
GOOGLE_CREDS_PATH = "credentials.json"


class VKPhotoBackup:
    """
    Класс для работы с API VK для резервного копирования фотографий.
    """

    def __init__(self, vk_token):
        """
        Инициализация класса с токеном VK.
        """
        self.vk_token = vk_token
        self.vk_url = 'https://api.vk.com/method/'
        self.api_version = '5.131'

    def get_albums(self, user_id):
        """
        Получение списка альбомов пользователя VK.

        :param user_id: ID пользователя VK.
        :return: Список альбомов пользователя.
        """
        params = {
            'access_token': self.vk_token,
            'v': self.api_version,
            'owner_id': user_id
        }
        response = requests.get(self.vk_url + 'photos.getAlbums', params=params).json()
        albums = response.get('response', {}).get('items', [])
        if not albums:
            print("Error fetching albums:", response.get('error', {}).get('error_msg'))
        else:
            for album in albums:
                print(f"- {album['title']} (ID: {album['id']})")
        return albums

    def get_photos(self, user_id, album_id, count=5):
        """
        Получение фотографий из альбома пользователя VK.

        :param user_id: ID пользователя VK.
        :param album_id: ID альбома.
        :param count: Количество фотографий для загрузки.
        :return: Отсортированный список фотографий.
        """
        params = {
            'access_token': self.vk_token,
            'v': self.api_version,
            'owner_id': user_id,
            'album_id': album_id,
            'extended': 1,
            'count': count
        }
        response = requests.get(self.vk_url + 'photos.get', params=params).json()
        photos = response.get('response', {}).get('items', [])
        return sorted(photos, key=lambda x: x['sizes'][-1]['width'] * x['sizes'][-1]['height'], reverse=True)[:count]


class YandexDiskUploader:
    """
    Класс для загрузки файлов на Яндекс.Диск.
    """

    def __init__(self, ya_token):

        self.ya_token = ya_token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/'

    def create_folder(self, folder_name):
        """
        Создание папки на Яндекс.Диске.

        :param folder_name: Название папки.
        """
        headers = {'Authorization': f'OAuth {self.ya_token}'}
        params = {'path': folder_name}
        response = requests.put(self.base_url + 'resources', headers=headers, params=params)
        if response.status_code == 409:
            print(f"Folder '{folder_name}' already exists on Yandex Disk.")
        elif response.status_code == 201:
            print(f"Folder '{folder_name}' created on Yandex Disk.")
        else:
            print(f"Error: {response.json()}")

    def upload_file(self, file_path, file_name, folder_name):
        """
        Загрузка файла на Яндекс.Диск.

        :param file_path: Локальный путь к файлу.
        :param file_name: Имя файла на Диске.
        :param folder_name: Папка на Яндекс.Диске.
        """
        headers = {'Authorization': f'OAuth {self.ya_token}'}
        upload_url = f"{self.base_url}resources/upload"
        params = {'path': f"{folder_name}/{file_name}", 'overwrite': 'true'}
        response = requests.get(upload_url, headers=headers, params=params).json()
        with open(file_path, 'rb') as file:
            requests.put(response['href'], files={'file': file})


class GoogleDriveUploader:
    """
    Класс для загрузки файлов на Google Drive.
    """

    def __init__(self, credentials_path):

        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=["https://www.googleapis.com/auth/drive"]
        )
        self.service = build('drive', 'v3', credentials=creds)

    def upload_file(self, file_path, file_name, folder_id):
        """
        Загрузка файла на Google Drive.

        :param file_path: Локальный путь к файлу.
        :param file_name: Имя файла на Google Drive.
        :param folder_id: ID папки на Google Drive.
        """
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"File {file_name} uploaded to Google Drive with ID {uploaded_file.get('id')}")


def backup_vk_photos(user_id, vk_token, ya_token, google_creds_path, storage_option, album_id, count=5,
                     folder_name='VK_Photos_Backup', google_folder_id=None):
    """
    Основная функция резервного копирования фотографий из VK на выбранный диск.

    :param user_id: ID пользователя VK.
    :param vk_token: Токен VK.
    :param ya_token: Токен Яндекс.Диска.
    :param google_creds_path: Путь к учетным данным Google.
    :param storage_option: Выбор хранилища ('yandex' или 'google').
    :param album_id: ID альбома.
    :param count: Количество фотографий.
    :param folder_name: Название папки на Яндекс.Диске.
    :param google_folder_id: ID папки на Google Drive. Только татая реализация .
                            Как реализовать так же  как для Яндекс.Диска - НЕ РАЗОБРАЛСЯ
    """
    vk_connector = VKPhotoBackup(vk_token)
    photos = vk_connector.get_photos(user_id, album_id, count)

    json_data = []  # Список для сбора информации о фото для JSON файла

    if storage_option == 'yandex':
        yandex = YandexDiskUploader(ya_token)
        if not folder_name:
            folder_name = 'VK_Photos_Backup'
        yandex.create_folder(folder_name)

        file_name_count = {}
        for photo in tqdm(photos, desc="Uploading photos to Yandex.Disk"):
            max_size_photo = max(photo['sizes'], key=lambda size: size['width'] * size['height'])
            photo_url = max_size_photo['url']
            likes = photo['likes']['count']
            if likes not in file_name_count:
                file_name_count[likes] = 0
            file_name_count[likes] += 1
            if file_name_count[likes] == 1:
                file_name = f"{likes}.jpg"
            else:
                file_name = f"{likes}({file_name_count[likes] - 1}).jpg"

            response = requests.get(photo_url)
            file_path = file_name
            with open(file_path, 'wb') as file:
                file.write(response.content)
            yandex.upload_file(file_path, file_name, folder_name)
            os.remove(file_path)
            json_data.append({"file_name": file_name, "size": max_size_photo['type']})

    elif storage_option == 'google':
        google = GoogleDriveUploader(google_creds_path)
        for photo in tqdm(photos, desc="Uploading photos to Google Drive"):
            max_size_photo = max(photo['sizes'], key=lambda size: size['width'] * size['height'])
            photo_url = max_size_photo['url']
            likes = photo['likes']['count']
            file_name = f"{likes}.jpg"
            response = requests.get(photo_url)
            file_path = file_name
            with open(file_path, 'wb') as file:
                file.write(response.content)
            google.upload_file(file_path, file_name, google_folder_id)
            os.remove(file_path)
            json_data.append({"file_name": file_name, "size": max_size_photo['type']})

    with open('photo_backup_metadata.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print("Metadata JSON file created as 'photo_backup_metadata.json'")


if __name__ == "__main__":
    user_id = input("Enter VK user ID: ")
    vk_backup = VKPhotoBackup(VK_TOKEN)
    print("Available albums:")
    albums = vk_backup.get_albums(user_id)

    album_id = input("Enter album ID for backup: ")
    count = input("Enter the number of photos to download (default 5): ")
    count = int(count) if count.isdigit() else 5

    storage_option = input("Choose storage (yandex/google): ").strip().lower()
    folder_name = input(
        "Enter Yandex Disk folder name (default VK_Photos_Backup): ") if storage_option == 'yandex' else None
    google_folder_id = input("Enter Google Drive folder ID: ") if storage_option == 'google' else None

    backup_vk_photos(user_id, VK_TOKEN, YA_TOKEN, GOOGLE_CREDS_PATH, storage_option, album_id, count, folder_name,
                     google_folder_id)