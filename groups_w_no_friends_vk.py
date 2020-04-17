import json
import requests
import time
import config
import datetime as dt
import sys

token = config.api_key


URL_GROUPS_GET = 'https://api.vk.com/method/groups.get'
URL_FRIENDS_GET = 'https://api.vk.com/method/friends.get'
URL2 = 'https://api.vk.com/method/users.get'
URL_GROUPS_GET_INFO = 'https://api.vk.com/method/groups.getById'


class TimeContextManager:
    def __init__(self):
        self.current_time = dt.datetime.today()

    def __enter__(self):
        print('Начало работы программы -', self.current_time.strftime('%H:%M:%S'))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = dt.datetime.today()
        print('Конец работы программы -', self.end_time.strftime('%H:%M:%S'))
        self.time_worked = self.end_time - self.current_time
        print('Время работы программы -', self.time_worked)


class VkUser:
    def __init__(self, id):
        try:
            user_info = get_user_id(id)
        except KeyError:
            print(f'Пользователя с id {id} нету')
            sys.exit()
        if id[0].isalpha():
            self.user_id = user_info['response'][0]['id']
            self.first_name = user_info['response'][0]['first_name']
            self.last_name = user_info['response'][0]['last_name']
        else:
            self.user_id = id
            self.first_name = user_info['response'][0]['first_name']
            self.last_name = user_info['response'][0]['last_name']
        self.user_groups = self.get_groups()
        print(f'added user id{self.user_id} {self.first_name} {self.last_name}')

    def get_groups(self):
        params = {
            'user_id': self.user_id,
            'access_token': token,
            'v': '5.52'
        }
        time.sleep(0.4)
        response = requests.get(URL_GROUPS_GET, params=params)
        print('~ get groups')
        json_ = response.json()
        # print(json_)
        try:
            json_['response']
        except KeyError:
            return 'error'
        return json_['response']['items']

    def get_friends(self):
        params = {
            'user_id': self.user_id,
            'access_token': token,
            'v': '5.52'
        }
        response = requests.get(URL_FRIENDS_GET, params=params)
        print('~ get friends')
        json_ = response.json()
        ids_list = json_['response']['items']
        users_list = []
        for user in ids_list:
            users_list.append(VkUser(str(user)))
            time.sleep(0.3)
        for user in users_list:
            if user.first_name == 'DELETED':
                users_list.remove(user)
            else:
                continue
        return users_list


def get_user_id(user):
    params = {
        'user_ids': user,
        'v': '5.52',
        'access_token': token
    }
    response = requests.get(URL2, params=params)
    print('~ get user info')
    time.sleep(0.4)
    json_ = response.json()

    return json_


def search(user):
    groups = user.get_groups()
    if groups == 'error':
        print(f'у пользователя {user.user_id} приватный профиль')
        sys.exit()
    friends = user.get_friends()
    groups_without_friends = []
    groups_left = len(groups)
    for group in groups:
        print(f'Групп осталось {groups_left}')
        friends_left = len(friends)
        for friend in friends:
            friends_groups = friend.user_groups
            if friends_groups == 'error':
                print(f'у пользователя {friend.user_id} приватный профиль')
                friends_left -= 1
                continue
            else:
                if group in friends_groups:
                    groups_left -= 1
                    break
                else:
                    friends_left -= 1
                    print(f'Проверить друзей для группы {group} осталось {friends_left}')
                    if friends_left == 0:
                        groups_without_friends.append(group)
                    else:
                        continue

    # print(groups_without_friends)
    list_to_json = []
    for group in groups_without_friends:
        params = {
            'group_id': group,
            'access_token': token,
            'v': '5.61'
        }
        response = requests.get(URL_GROUPS_GET_INFO, params=params)
        time.sleep(0.4)
        response2 = requests.get(URL_GROUPS_GET_MEMBERS, params=params)
        time.sleep(0.4)
        json_ = response.json()
        json_2 = response2.json()
        group_info = {
            'name': json_['response'][0]['name'],
            'gid': json_['response'][0]['id'],
            'members_count': json_2['response']['count']
        }
        list_to_json.append(group_info)
    print(list_to_json)
    return list_to_json


if __name__ == '__main__':
    # config.get_token()
    with TimeContextManager():
        user = VkUser(input('Введите id - '))
        with open('groups.json', 'w', encoding='utf8') as f:
            to_json = search(user)
            f.write(json.dumps(to_json))
