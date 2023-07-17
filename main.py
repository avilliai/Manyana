# -*- coding:utf-8 -*-
import datetime
import json

import yaml
from mirai import Mirai, FriendMessage, WebSocketAdapter

from run import poeAi

if __name__ == '__main__':
    with open('config.json','r',encoding='utf-8') as fp:
        data=fp.read()
    config=json.loads(data)
    qq=int(config.get('botQQ'))
    key=config.get("vertify_key")
    port= int(config.get("port"))
    bot = Mirai(qq, adapter=WebSocketAdapter(
        verify_key=key, host='localhost', port=port
    ))


    botName = config.get('botName')
    master=int(config.get('master'))

    @bot.on(FriendMessage)
    async def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            await bot.send(event, 'Hello World!')




    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+" 读取到apiKey列表")

    def startVer():
        file_object = open("./mylog.log")
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()
        print(all_the_text)

    poeAi.main(bot,master,result.get("poe-api"),result.get("proxy"))
    startVer()
    bot.run()