import json
def file_writer(json_):
    with open('groups.json', 'w', encoding='utf8') as f:
        f.write(json.dumps(json_, ensure_ascii=False))  # to json file
        print('Информация успешно загруженна')