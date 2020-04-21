from vk_api import apivk
from time_check import TimeContextManager
from result_writer import file_writer

if __name__ == '__main__':
    with TimeContextManager():
        user = apivk.VkUser(input('Введите id - '))
        to_json = user.search()
        file_writer(to_json)
