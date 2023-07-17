# -*- coding:utf-8 -*-
import datetime
import yaml
from mirai import Mirai, FriendMessage, WebSocketAdapter

from run import poeAi

if __name__ == '__main__':
    bot = Mirai(12345678, adapter=WebSocketAdapter(
        verify_key='your_verify_key', host='localhost', port=6090
    ))

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

    poeAi.main(bot,result.get("poe-api"))
    startVer()
    bot.run()