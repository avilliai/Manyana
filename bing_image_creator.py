# -*- coding:utf-8 -*-
import os
import sys

#下面的两行是launcher启动必要设置，勿动。
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import yaml
from mirai import Mirai, WebSocketAdapter, GroupMessage, Image

from plugins.bingImageCreater.bingDraw import bingCreate
from plugins.toolkits import newLogger


def main(bot, logger):
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    sock5proxy = resulttr.get("sock5-proxy")
    bing_image_creator_key = resulttr.get("bing-image-creator")

    @bot.on(GroupMessage)
    async def selfBingDraw(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag = str(event.message_chain).replace("画 ", "")
            list1 = ["sex", "nsfw", "性交", "做爱", "pussy", "奴隶", "调教", "中出", "后入", "颜射", "阴道", "NSFW",
                     "SEX", "Sex"]
            for i in list1:
                if i in tag:
                    await bot.send(event, "审核策略生效，请检查并去除prompt中违规内容")
                    return
            if bing_image_creator_key.get("_U") != "" and bing_image_creator_key.get("KievRPSSecAuth") != "":
                try:
                    logger.info(f"bing接口发起请求:{tag}")
                    p = await bingCreate(sock5proxy, tag, bing_image_creator_key.get("_U"),
                                         bing_image_creator_key.get("KievRPSSecAuth"))
                    plist = []
                    for i in p:
                        plist.append(Image(path=i))
                    await bot.send(event, plist, True)
                except Exception as e:
                    logger.error(e)
                    await bot.send(event, "出错，请重试；可能是bing cookie过期，请检查")


if __name__ == '__main__':
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    sock5proxy = resulttr.get("sock5-proxy")
    bing_image_creator_key = resulttr.get("bing-image-creator")
    if bing_image_creator_key.get("_U") != "" and bing_image_creator_key.get("KievRPSSecAuth") != "":
        with open('config.json', 'r', encoding='utf-8') as f:
            data = yaml.load(f.read(), Loader=yaml.FullLoader)

        config = data
        qq = int(config.get('botQQ'))
        key = config.get("vertify_key")
        port = int(config.get("port"))
        bot = Mirai(qq, adapter=WebSocketAdapter(
            verify_key=key, host='localhost', port=port
        ))
        logger = newLogger()
        main(bot, logger)
        bot.run(asgi_server=None)
