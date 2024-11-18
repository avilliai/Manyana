# -*- coding: utf-8 -*-
import os
import random
import httpx
import json
import base64
from io import BytesIO
from PIL import Image as PILImage
import asyncio

import yaml
from mirai import GroupMessage
from mirai import Image

from plugins.toolkits import random_str

from plugins.setuModerate import fileImgModerate, pic_audit_standalone
from plugins.aiDrawer import getloras, SdDraw, draw2, airedraw, draw1, draw3, tiktokredraw, draw5, draw4, draw6, fluxDrawer, SdDraw1, SdDraw2, getcheckpoints, ckpt2, SdreDraw

i = 0
turn = 0
UserGet = {}

def main(bot, logger):
    logger.info("ai绘画 启用")
    i = 0
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
    global UserGet
    UserGet = {}

    @bot.on(GroupMessage)
    async def msDrawer(event: GroupMessage):
        if str(event.message_chain).startswith("画") and aiDrawController.get("modelscopeSD"):
            tag = str(event.message_chain).split("画")[1]
            logger.info("发起modelscope SDai绘画请求，prompt:" + tag)
            try:
                p = await fluxDrawer(tag)
                await bot.send(event, ["modelscope flux api result:",Image(url=p)], True)
            except Exception as e:
                logger.error(e)
                logger.error("modelscope Drawer出错")
                #await bot.send(event,"只因了喵~别急，不是sd喵~")       

    @bot.on(GroupMessage)
    async def AiSdDraw(event: GroupMessage):
        global turn
        if str(event.message_chain).startswith("画 ") and sdUrl!="" and sdUrl!=" ":
            tag = str(event.message_chain).replace("画 ", "")
            path = f"data/pictures/cache/{random_str()}.png"
            logger.info(f"发起SDai绘画请求，path:{path}|prompt:{tag}")
            try:
                await bot.send(event, f'sd前面排队{turn}人，请耐心等待喵~', True)
                turn += 1
                # 没啥好审的，controller直接自个写了。
                p = await SdDraw(tag + positive_prompt, negative_prompt, path, sdUrl, event.group.id)
                # logger.error(str(p))
                if p == False:
                    turn -= 1
                    logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                else:
                    await bot.send(event, [Image(path=path)], True)
                    turn -= 1
                    # logger.info("success")
                    #await bot.send(event, "防出色图加上rating_safe，如果色图请自行撤回喵~")
            except Exception as e:
                logger.error(e)
                turn -= 1
                await bot.send(event,"sd只因了，联系master喵~")
                
        if str(event.message_chain) == "lora" and aiDrawController.get("sd接口"):   #获取lora列表
            logger.info('查询loras中...')
            try:
                p = await getloras(sdUrl)
                logger.info(str(p))
                await bot.send(event, p, True)
                # logger.info("success")
            except Exception as e:
                logger.error(e)
                
        if str(event.message_chain) == "ckpt" and aiDrawController.get("sd接口"):   #获取lora列表
            logger.info('查询checkpoints中...')
            try:
                p = await getcheckpoints(sdUrl)
                logger.info(str(p))
                await bot.send(event, p, True)
                # logger.info("success")
            except Exception as e:
                logger.error(e)
        
        if str(event.message_chain).startswith("画横图 ") and aiDrawController.get("sd接口"):
            tag = str(event.message_chain).replace("画横图 ", "")
            path = f"data/pictures/cache/{random_str()}.png"
            logger.info(f"发起SDai绘画请求，path:{path}|prompt:{tag}")
            try:
                await bot.send(event, f"开始画横图啦~sd前面排队{turn}人，请耐心等待喵~", True)
                turn += 1
                # 没啥好审的，controller直接自个写了。
                p = await SdDraw1(tag + positive_prompt, negative_prompt, path, sdUrl, event.group.id)
                # logger.error(str(p))
                if p == False:
                    turn -= 1
                    logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                else:
                    await bot.send(event, [Image(path=path)], True)
                    turn -= 1
                    # logger.info("success")
                    #await bot.send(event, "防出色图加上rating_safe，如果色图请自行撤回喵~")
            except Exception as e:
                logger.error(e)
                turn -= 1
                await bot.send(event,"sd只因了，联系master喵~")
                
        if str(event.message_chain).startswith("画方图 ") and aiDrawController.get("sd接口"):
            tag = str(event.message_chain).replace("画方图 ", "")
            path = f"data/pictures/cache/{random_str()}.png"
            logger.info(f"发起SDai绘画请求，path:{path}|prompt:{tag}")
            try:
                await bot.send(event, f"开始画方图啦~sd前面排队{turn}人，请耐心等待喵~", True)
                turn += 1
                # 没啥好审的，controller直接自个写了。
                p = await SdDraw2(tag + positive_prompt, negative_prompt, path, sdUrl, event.group.id)
                # logger.error(str(p))
                if p == False:
                    turn -= 1
                    logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                else:
                    await bot.send(event, [Image(path=path)], True)
                    turn -= 1
                    # logger.info("success")
                    #await bot.send(event, "防出色图加上rating_safe，如果色图请自行撤回喵~")
            except Exception as e:
                logger.error(e)
                turn -= 1
                await bot.send(event,"sd只因了，联系master喵~")
                
        if str(event.message_chain).startswith("ckpt2 ") and aiDrawController.get("sd接口"):
            tag = str(event.message_chain).replace("ckpt2 ", "")
            logger.info('切换ckpt中')
            try:
                await ckpt2(tag)
                await bot.send(event, "切换成功喵~第一次会慢一点~", True)
                # logger.info("success")
            except Exception as e:
                logger.error(e)
                await bot.send(event, "ckpt切换失败", True)

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
                    await bot.send(event, [Image(path=p[0]), Image(path=p[1]), Image(path=p[2]), Image(path=p[3])],True)                   
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
            

    @bot.on(GroupMessage)
    async def sdreDrawRun(event: GroupMessage):
        global UserGet
        global turn

        if event.message_chain.has(Image) == False and (str(event.message_chain) == ("重绘") or str(event.message_chain).startswith("重绘 ")):
            prompt = str(event.message_chain).replace("重绘", "").strip()
            UserGet[event.sender.id] = [prompt]
            await bot.send(event, "请发送要重绘的图片")

        # 处理图片和重绘命令
        if (str(event.message_chain).startswith("重绘") or event.sender.id in UserGet) and event.message_chain.count(Image):
            if (str(event.message_chain).startswith("重绘")) and event.message_chain.count(Image):
                prompt = str(event.message_chain).replace("重绘", "").strip()
                UserGet[event.sender.id] = [prompt]

            # 日志记录
            prompts = ', '.join(UserGet[event.sender.id])
            logger.info(f"接收来自群：{event.group.id} 用户：{event.sender.id} 的重绘指令 prompt: {prompts}")

            # 获取图片路径
            path = f"data/pictures/cache/{random_str()}.png"
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            logger.info(f"发起SDai重绘请求，path:{path}|prompt:{prompts}")
            prompts_str = ' '.join(UserGet[event.sender.id]) + ' ' + positive_prompt
            UserGet.pop(event.sender.id)
            

            try:
                b64_in = await url_to_base64(img_url)
                
                await bot.send(event, f"开始重绘啦~sd前面排队{turn}人，请耐心等待喵~", True)
                turn += 1
                # 将 UserGet[event.sender.id] 列表中的内容和 positive_prompt 合并成一个字符串
                p = await SdreDraw(prompts_str, negative_prompt, path, sdUrl, event.group.id, b64_in)
                if p == False:
                    turn -= 1
                    logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                else:
                    await bot.send(event, [Image(path=path)], True)
                    turn -= 1
            except Exception as e:
                logger.error(f"重绘失败: {e}")
                turn -= 1
                await bot.send(event, "重绘失败了喵~", True)

    async def url_to_base64(url):
        async with httpx.AsyncClient(timeout=9000) as client:
            response = await client.get(url)
            if response.status_code == 200:
                image_bytes = response.content
                encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                return encoded_string
            else:
                raise Exception(f"Failed to retrieve image: {response.status_code}")
            
