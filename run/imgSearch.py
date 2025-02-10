# -*- coding: utf-8 -*-

import yaml
from mirai import GroupMessage
from mirai import Image, MessageChain
from mirai.models import ForwardMessageNode, Forward

from plugins.imgSearch import fetch_results
from plugins.toolkits import picDwn, random_str


def main(bot, api_key, proxy, logger):
    logger.info("搜图功能启动完毕")
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    cookies = result.get("e-hentai")
    proxy=result.get("proxy")
    sauceno_api=result.get("sauceno-api")
    if proxy=="" or proxy==" ":
        proxy=None
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
    selfsensor = result1.get("moderate").get("selfsensor")
    selfthreshold = result1.get("moderate").get("selfthreshold")
    global dataGet
    dataGet = {}
    global userSearch

    @bot.on(GroupMessage)
    async def startYourSearch(event: GroupMessage):
        global dataGet
        if str(event.message_chain) == "搜图":
            await bot.send(event, "请发送要搜索的图片")
            dataGet[event.sender.id] = []

    @bot.on(GroupMessage)
    async def imgSearcher(event: GroupMessage):
        global dataGet
        if ("搜图" in str(event.message_chain) or event.sender.id in dataGet) and event.message_chain.count(Image):
            logger.info("接收来自群：" + str(event.group.id) + " 用户：" + str(event.sender.id) + " 的搜图指令")
            dataGet[event.sender.id] = []
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            results = await fetch_results(proxy, img_url,sauceno_api)
            dataGet.pop(event.sender.id)
            forMeslist=[]
            for name, result in results.items():
                if result and result[0]!="":

                    logger.info(f"{name} 成功返回: {result}")
                    try:
                        path="data/pictures/cache/" + random_str() + ".png"
                        imgpath=await picDwn(result[0],path,proxy)
                        b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([ Image(path=imgpath),result[1] ]))
                    except Exception as e:
                        logger.error(f"预览图{name} 下载失败: {e}")
                        b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([ Image(url=result[0]),result[1] ]))
                    if name=="ascii2d_async":
                        b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([Image(url=img_url), result[1]]))
                    forMeslist.append(b1)
                else:
                    logger.error(f"{name} 返回失败或无结果")
                    b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                            message_chain=MessageChain([f"{name} 返回失败或无结果"]))
                    forMeslist.append(b1)
            await bot.send(event, Forward(node_list=forMeslist))