import json
import sys
import time
from vk_api import constants
from time_check import TimeContextManager
from result_writer import file_writer


class VkUser:
    def __init__(self, user_id):
        user_info = self.check_user_id(user_id)
        if 'deactivated' in user_info['response'][0]:
            print(f'Пользователь {user_info["response"][0]["id"]} удален или забанен')
            self.user_id = 'deactivated'
        else:
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
        json_ = constants.VkApi().get_response('groups.get', {'user_id': self.user_id})
        print('~ get groups')
        try:
            json_['response']
        except KeyError:
            return 'error'
        return json_['response']['items']

    def get_friends(self):
        json_ = constants.VkApi().get_response('friends.get', {'user_id': self.user_id})
        print('~ get friends')
        ids_list = json_['response']['items']
        users_list = []
        user_ids_list = []
        for user_id in ids_list:
            users_list.append(VkUser(str(user_id)))
            time.sleep(0.3)
        for vk_user in users_list:
            if vk_user.user_id == 'deactivated':
                pass
            else:
                user_ids_list.append(vk_user.user_id)
        return user_ids_list

    def search(self):
        groups = self.get_groups()
        if groups == 'error':
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
        for group in groups_without_friends:
            json_ = constants.VkApi().get_response('groups.getById', {'group_id': group})
            print('~ get group info')
            json_2 = constants.VkApi().get_response('groups.getMembers', {'group_id': group})
            print('~ get group members')
            group_info = {
                'name': json_['response'][0]['name'],
                'gid': json_['response'][0]['id'],
                'members_count': json_2['response']['count']
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
            json_ = constants.VkApi().get_response('execute', {'code': code})
            print('~ execute')
            response_list.append(json_)
        groups_list = []
        for resp in response_list:
            for item in resp['response']:
                try:
                    groups_list.extend(item['items'])
                except TypeError:
                    print('Приватный профиль')
        groups_list = list(set(groups_list))
        return groups_list

    def check_user_id(self, user_id):
        user_info = constants.VkApi().get_response('users.get', {'user_ids': user_id})
        print('~ get user info')
        try:
            user_info['response']
            # Проверяем правильность введенного id
        except KeyError:
            print(f'Пользователя с id {user_id} нету')
            sys.exit()
        return user_info


if __name__ == '__main__':
    with TimeContextManager():
        user = VkUser(input('Введите id - '))
        to_json = user.search()
        file_writer(to_json)
