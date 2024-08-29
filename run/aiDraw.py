# -*- coding: utf-8 -*-
import os
import random

import yaml
from mirai import GroupMessage
from mirai import Image

from plugins.toolkits import random_str

from plugins.setuModerate import fileImgModerate
from plugins.aiDrawer import SdDraw, draw2, airedraw, draw1, draw3, tiktokredraw, draw5, draw4, draw6, fluxDrawer


def main(bot, logger):
    logger.info("ai绘画 启用")
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    moderateK = result.get("moderate")
    proxy = result.get("proxy")
    sdUrl = result.get("sdUrl")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
    selfsensor = result1.get("moderate").get("selfsensor")
    selfthreshold = result1.get("moderate").get("selfthreshold")
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller = yaml.load(f.read(), Loader=yaml.FullLoader)
    aiDrawController = controller.get("ai绘画")
    negative_prompt = aiDrawController.get("negative_prompt")
    positive_prompt = aiDrawController.get("positive_prompt")
    global redraw
    redraw = {}

    @bot.on(GroupMessage)
    async def msDrawer(event: GroupMessage):
        if str(event.message_chain).startswith("画 ") and aiDrawController.get("modelscopeSD"):
            tag = str(event.message_chain).replace("画 ", "")
            logger.info("发起modelscope SDai绘画请求，prompt:" + tag)
            try:
                p = await fluxDrawer(tag)
                await bot.send(event, Image(url=p), True)
            except Exception as e:
                logger.error(e)
                logger.error("modelscope Drawer出错")
                await bot.send(event,"寄了喵",True)

    @bot.on(GroupMessage)
    async def AiSdDraw(event: GroupMessage):
        if str(event.message_chain).startswith("画 ") and aiDrawController.get("sd接口"):
            tag = str(event.message_chain).replace("画 ", "")
            path = f"data/pictures/cache/{random_str()}.png"
            logger.info(f"发起SDai绘画请求，path:{path}|prompt:{tag}")
            try:
                # 没啥好审的，controller直接自个写了。
                p = await SdDraw(tag + positive_prompt, negative_prompt, path, sdUrl)
                # logger.error(str(p))

                await bot.send(event, [Image(path=path)], True)
                # logger.info("success")
            except Exception as e:
                logger.error(e)

    @bot.on(GroupMessage)
    async def aidrawf1(event: GroupMessage):
        if str(event.message_chain).startswith("画 ") and aiDrawController.get("接口1"):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            logger.info("发起ai绘画请求，path:" + path + "|prompt:" + tag)
            i = 1
            while i < 8:
                try:
                    logger.info(f"接口1绘画中......第{i}次请求....")
                    p = await draw1(tag, path)
                    logger.error(str(p))
                    await bot.send(event, [Image(path=p[0]), Image(path=p[1]), Image(path=p[2]), Image(path=p[3])],
                                   True)
                except Exception as e:
                    logger.error(e)
                    logger.error("接口1绘画失败.......")
                    i += 1
                    # await bot.send(event,"接口1绘画失败.......")

    @bot.on(GroupMessage)
    async def aidrawff2(event: GroupMessage):
        if str(event.message_chain).startswith("画 ") and aiDrawController.get("接口2"):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                logger.info("接口2绘画中......")
                p = await draw2(tag, path)
                if selfsensor:
                    try:
                        thurs = await fileImgModerate(path, moderateK)
                        logger.info(f"获取到审核结果： adult- {thurs}")
                        if int(thurs) > selfthreshold:
                            logger.warning(f"不安全的图片，自我审核过滤")
                            await bot.send(event, ["nsfw内容已过滤", Image(
                                path="data/colorfulAnimeCharacter/" + random.choice(
                                    os.listdir("data/colorfulAnimeCharacter")))])
                            return
                    except Exception as e:
                        logger.error(e)
                        logger.error("无法进行自我审核，错误的网络环境或apikey")
                        return
                await bot.send(event, Image(path=p), True)
            except Exception as e:
                logger.error(e)
                logger.error("接口2绘画失败.......")
                # await bot.send(event,"接口2绘画失败.......")

    @bot.on(GroupMessage)
    async def aidrawff3(event: GroupMessage):
        if str(event.message_chain).startswith("画 ") and aiDrawController.get("接口3"):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            if len(tag) > 100:
                return
            try:
                logger.info("接口3绘画中......")
                p = await draw3(tag, path)
                if selfsensor:
                    try:
                        thurs = await fileImgModerate(path, moderateK)
                        logger.info(f"获取到审核结果： adult- {thurs}")
                        if int(thurs) > selfthreshold:
                            logger.warning(f"不安全的图片，自我审核过滤")
                            await bot.send(event, ["nsfw内容已过滤", Image(
                                path="data/colorfulAnimeCharacter/" + random.choice(
                                    os.listdir("data/colorfulAnimeCharacter")))])
                            return
                    except Exception as e:
                        logger.error(e)
                        logger.error("无法进行自我审核，错误的网络环境或apikey")
                        return
                await bot.send(event, Image(path=p), True)
            except Exception as e:
                logger.error(e)
                logger.error("接口3绘画失败.......")

    @bot.on(GroupMessage)
    async def aidrawff4(event: GroupMessage):
        if str(event.message_chain).startswith("画 ") and aiDrawController.get("接口5"):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                logger.info("接口5绘画中......")
                p = await draw5(tag, path)
                if selfsensor:
                    try:
                        thurs = await fileImgModerate(path, moderateK)
                        logger.info(f"获取到审核结果： adult- {thurs}")
                        if int(thurs) > selfthreshold:
                            logger.warning(f"不安全的图片，自我审核过滤")
                            await bot.send(event, ["nsfw内容已过滤", Image(
                                path="data/colorfulAnimeCharacter/" + random.choice(
                                    os.listdir("data/colorfulAnimeCharacter")))])
                            return
                    except Exception as e:
                        logger.error(e)
                        logger.error("无法进行自我审核，错误的网络环境或apikey")
                        return
                await bot.send(event, Image(path=p), True)
            except Exception as e:
                logger.error(e)
                logger.error("接口5绘画失败.......")

    @bot.on(GroupMessage)
    async def aidrawff4(event: GroupMessage):
        if str(event.message_chain).startswith("画 ") and aiDrawController.get("接口6"):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            i = 0
            while i < 5:
                try:
                    logger.info("接口6绘画中......")
                    p = await draw6(tag, path)
                    if selfsensor:
                        try:
                            thurs = await fileImgModerate(p, moderateK)
                            logger.info(f"获取到审核结果： adult- {thurs}")
                            if int(thurs) > selfthreshold:
                                logger.warning(f"不安全的图片，自我审核过滤")
                                await bot.send(event, ["nsfw内容已过滤", Image(
                                    path="data/colorfulAnimeCharacter/" + random.choice(
                                        os.listdir("data/colorfulAnimeCharacter")))])
                                return
                        except Exception as e:
                            logger.error(e)
                            logger.error("无法进行自我审核，错误的网络环境或apikey")
                            return
                    await bot.send(event, Image(path=p), True)
                    return
                except Exception as e:
                    logger.error(e)
                    logger.error("接口6绘画失败.......")
                    i += 1

    @bot.on(GroupMessage)
    async def aidrawff5(event: GroupMessage):
        if str(event.message_chain).startswith("画 ") and aiDrawController.get("接口4"):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                logger.info("接口4绘画中......")
                p = await draw4(tag, path)
                if selfsensor:
                    try:
                        thurs = await fileImgModerate(path, moderateK)
                        logger.info(f"获取到审核结果： adult- {thurs}")
                        if int(thurs) > selfthreshold:
                            logger.warning(f"不安全的图片，自我审核过滤")
                            await bot.send(event, ["nsfw内容已过滤", Image(
                                path="data/colorfulAnimeCharacter/" + random.choice(
                                    os.listdir("data/colorfulAnimeCharacter")))])
                            return
                    except Exception as e:
                        logger.error(e)
                        logger.error("无法进行自我审核，错误的网络环境或apikey")
                        await bot.send(event, ["审核策略失效，为确保安全，不显示本图片", Image(
                            path="data/colorfulAnimeCharacter/" + random.choice(
                                os.listdir("data/colorfulAnimeCharacter")))])
                        return
                await bot.send(event, Image(path=p), True)
            except Exception as e:
                logger.error(e)
                logger.error("接口4绘画失败.......")

    @bot.on(GroupMessage)
    async def rededd(event: GroupMessage):
        global redraw
        if str(event.message_chain).startswith("以图生图 ") and aiDrawController.get("ai重绘"):
            await bot.send(event, "请发送图片，bot随后将开始绘制")
            redraw[event.sender.id] = str(event.message_chain).replace("以图生图 ", "")

    @bot.on(GroupMessage)
    async def redrawStart(event: GroupMessage):
        global redraw
        if event.message_chain.count(Image) and event.sender.id in redraw:
            prompt = redraw.get(event.sender.id)
            lst_img = event.message_chain.get(Image)
            url1 = lst_img[0].url
            logger.info(f"以图生图,prompt:{prompt} url:{url1}")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                p = await airedraw(prompt, url1, path)
                await bot.send(event, Image(path=p))
            except Exception as e:
                logger.error(e)
                logger.error("ai绘画出错")
                await bot.send(event, "接口1绘画出错")
            try:
                p = await tiktokredraw(prompt, url1, path)
                await bot.send(event, Image(path=p))
            except Exception as e:
                logger.error(e)
                logger.error("ai绘画出错")
                await bot.send(event, "接口2绘画出错")
            redraw.pop(event.sender.id)
