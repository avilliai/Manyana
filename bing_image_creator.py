# -*- coding:utf-8 -*-
import sys

import yaml
from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, At, Startup, FriendMessage, Shutdown

from plugins.bingImageCreater.bingDraw import bingCreate
from plugins.newLogger import newLogger


def main(bot,logger):
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    sock5proxy=resulttr.get("sock5-proxy")
    bing_image_creator_key=resulttr.get("bing-image-creator")
    @bot.on(GroupMessage)
    async def selfBingDraw(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag = str(event.message_chain).replace("画 ", "")
            if bing_image_creator_key.get("_U")!="" and bing_image_creator_key.get("KievRPSSecAuth")!="":
                try:
                    logger.info(f"bing接口发起请求:{tag}")
                    p=await bingCreate(sock5proxy,tag,bing_image_creator_key.get("_U"),bing_image_creator_key.get("KievRPSSecAuth"))
                    plist=[]
                    for i in p:
                        plist.append(Image(path=i))
                    await bot.send(event, plist, True)
                except Exception as e:
                    logger.error(e)
                    await bot.send(event,"bing cookie过期，请检查")
if __name__ == '__main__':
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    sock5proxy=resulttr.get("sock5-proxy")
    bing_image_creator_key=resulttr.get("bing-image-creator")
    if bing_image_creator_key.get("_U") != "" and bing_image_creator_key.get("KievRPSSecAuth") != "":
        with open('config.json', 'r', encoding='utf-8') as f:
            data = yaml.load(f.read(), Loader=yaml.FullLoader)

        config=data
        qq=int(config.get('botQQ'))
        key=config.get("vertify_key")
        port= int(config.get("port"))
        bot = Mirai(qq, adapter=WebSocketAdapter(
            verify_key=key, host='localhost', port=port
        ))
        logger = newLogger()
        main(bot,logger)
        bot.run()
