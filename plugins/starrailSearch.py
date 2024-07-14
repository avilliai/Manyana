# -*- coding: utf-8 -*-
import json

file = open('./data/star-rail-atlas/othername.json', 'r', encoding="utf-8")
js = file.read()
origindata = json.loads(js)

file = open("./data/star-rail-atlas/path.json", 'r', encoding="utf-8")
js = file.read()
picData = json.loads(js)


def find_keys_containing_value(json_data, search_value):
    result = []

    def search_in_dict(d, current_path=[]):
        if isinstance(d, dict):
            for key, value in d.items():
                search_in_dict(value, current_path + [key])
        elif isinstance(d, list):
            if search_value in d:
                result.append(current_path)
        else:
            if search_value == d:
                result.append(current_path[:-1])

    search_in_dict(json_data)
    return result


def getxinqiuPath(search_value):
    result = find_keys_containing_value(origindata, search_value)

    # 打印结果
    for path in result:
        p = "/".join(path)
    r = picData.get(p.split("/")[0]).get(p.split("/")[1])
    return "data/star-rail-atlas/" + r
