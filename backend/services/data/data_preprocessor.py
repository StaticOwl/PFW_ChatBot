import os

from backend.utils.data_utils import update_keys_with_substring, insert_newline


def update_json_structure(json_data):
    if json_data[-1]['title'] == 'dummy':
        json_data['scrapped_data'].pop(-1)
    updated_json = []
    data_dict = {}
    data_key = []
    json_data.append({'title': 'dummy', 'type': 'dummy', 'context': 'dummy'})
    for data in json_data:
        if (data['title'], data['type']) not in data_key or data == json_data[-1]:
            if data_dict:
                updated_json.append(data_dict)
            data_dict = {'title': data['title'].strip(), 'type': data['type'].strip()}
            if 'count' in data:
                data_dict['count'] = data['count']
            data_key.append((data['title'], data['type']))

        context_data = data['context'].split(" ")
        new_key = context_data[0].lower()
        new_value = " ".join(context_data[1:])
        data_dict[new_key] = new_value.replace('\n', '')

    return updated_json


def textify_data(big_data, configs: dict = None):
    content = ""
    for data in big_data:
        data_type = data['type']
        config = configs.get(data_type).get('textify')
        text_config_type = configs.get(data_type).get('text_config_type')
        if text_config_type == 'multi':
            count = int(data['count'])
            for i in range(count):
                config = update_keys_with_substring(config, 'iter', str(i))
        for key, value in data.items():
            if key in config:
                content += config[key].format(**data)

        content += "\n\n"

    with open(os.getenv("TRAINING_CONTEXT"), 'w+') as f:
        f.write(insert_newline(content, int(os.getenv("MAX_CHARS"))))
