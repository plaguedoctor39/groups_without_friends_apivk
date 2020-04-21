from vk_api import constants
import requests
import time
import json
import sys


class VkApi:
    API_VERSION_VK = constants.API_VERSION_VK
    URL_VK = constants.URL_VK
    TOKEN = constants.api_key
    PARAMS = constants.PARAMS

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


class VkUser(VkApi):
    def __init__(self, user_id):
        user_info = self.check_user_id(user_id)
        if user_id[0].isalpha():
            self.user_id = user_info['response'][0]['id']
            self.first_name = user_info['response'][0]['first_name']
            self.last_name = user_info['response'][0]['last_name']
        else:
            self.user_id = user_id
            self.first_name = user_info['response'][0]['first_name']
            self.last_name = user_info['response'][0]['last_name']
        print(f'added user id{self.user_id} {self.first_name} {self.last_name}')

    def get_groups(self):
        json_ = VkApi().get_response('groups.get', {'user_id': self.user_id})
        print('~ get groups')
        try:
            json_['response']
        except KeyError:
            return []
        return json_['response']['items']

    def get_friends(self):
        json_ = VkApi().get_response('friends.get', {'user_id': self.user_id})
        print('~ get friends')
        ids_list = json_['response']['items']
        # users_list = []
        # user_ids_list = []
        # for user_id in ids_list:
        #     users_list.append(VkUser(str(user_id)))
        #     time.sleep(0.3)
        # for vk_user in users_list:
        #     if vk_user.user_id == 'deactivated':
        #         pass
        #     else:
        #         user_ids_list.append(vk_user.user_id)
        return ids_list

    def search(self):
        groups = self.get_groups()
        if len(groups) == 0:
            print(f'у пользователя {self.user_id} приватный профиль')
            sys.exit()
        groups_list = self.do_execute()
        groups_without_friends = []
        for group in groups:
            if group in groups_list:
                pass
            else:
                groups_without_friends.append(group)

        list_to_json = []
        response_list = []
        groups_len = len(groups_without_friends) // 500
        for i in range(groups_len + 1):
            code_groups = f"var groups = {groups_without_friends};"
            code = """var groups_info = [];
            groups_info.push(API.groups.getById({"group_ids": groups, "fields": "members_count"}));
                return groups_info;"""
            code = code_groups + code
            json_2 = VkApi().get_response('execute', {'code': code})
            print('~ execute groups')
            response_list.append(json_2)
        for resp in response_list:
            for item in resp['response']:
                for group in item:
                    group_info = {
                        'name': group['name'],
                        'gid': group['id'],
                        'members_count': group['members_count']
                    }
                    list_to_json.append(group_info)
        return list_to_json

    def do_execute(self):
        friends_list = self.get_friends()
        itter = len(friends_list) // 25
        execute_list = [[] * 25] * (itter + 1)
        tmp = []
        list_id = 0
        response_list = []
        for friend_list in range(itter + 1):
            for i in range(25):
                if list_id < len(friends_list):
                    tmp.append(friends_list[list_id])
                    list_id += 1
                else:
                    break
            execute_list[friend_list] = tmp
            tmp = []
        for i in range(itter):
            code_friends = f"var friends = {execute_list[i]};"
            code = """var groups = [];
            var i = 0;
            while (i < friends.length) {
                groups.push(API.groups.get({"user_id": friends[i], "extended": 0}));
                i = i + 1;
            };
            return groups;"""
            code = code_friends + code
            json_ = VkApi().get_response('execute', {'code': code})
            print('~ execute friends')
            response_list.append(json_)
        groups_list = []
        for resp in response_list:
            for item in resp['response']:
                try:
                    groups_list.extend(item['items'])
                except TypeError:
                    print('Не смог получить доступ к группам')
        groups_list = list(set(groups_list))
        return groups_list

    def check_user_id(self, user_id):
        user_info = VkApi().get_response('users.get', {'user_ids': user_id})
        print('~ get user info')
        try:
            user_info['response']
            # Проверяем правильность введенного id
            if 'deactivated' in user_info['response'][0]:
                print(f'Пользователь {user_info["response"][0]["id"]} удален или забанен')
                sys.exit()
            else:
                pass
        except KeyError:
            # print(user_info)
            print(f'Пользователя с id {user_id} нету')
            sys.exit()
        return user_info
