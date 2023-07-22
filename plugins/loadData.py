import datetime
import json

import yaml


def loadUser():
    file = open('data/music/groups.txt', 'r')
    js = file.read()
    severGroupsa = json.loads(js)

    with open('data/userData.yaml', 'r',encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    # 修改为你bot的名字
    userdict = data
    userCount = userdict.keys()

    time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(time1 + '| 功能已加载完毕，正在连接mirai-api-http(如出现WARNING可忽略)')
    return [time1 + '| 已读取服务群聊:' + str(len(severGroupsa)) + '个', time1 + '| 已读取有记录用户:' + str(len(userCount)) + '个',
            time1 + '| 功能已加载完毕，欢迎使用']
