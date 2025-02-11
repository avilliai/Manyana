# -*- coding: utf-8 -*-
import asyncio
import base64
import os
import random
from io import BytesIO

import httpx
import yaml
from bs4 import BeautifulSoup
from mirai import GroupMessage
from mirai import Image, MessageChain
from mirai.models import ForwardMessageNode, Forward

from plugins.aiDrawer import getloras, SdDraw, draw2, airedraw, draw1, draw3, tiktokredraw, draw5, draw4, draw6, \
    fluxDrawer, SdDraw1, SdDraw2, getcheckpoints, ckpt2, SdreDraw, SdDraw0, \
    cn1, n4, n3, bing_dalle3, flux_ultra
from plugins.setuModerate import fileImgModerate, pic_audit_standalone
from plugins.toolkits import random_str

i = 0
turn = 0
UserGet = {}
tag_user = {}
sd_user_args = {}
sd_re_args = {}
UserGet1 = {}


def main(bot, logger):
    logger.info("ai绘画 启用")
    i = 0
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    moderateK = result.get("moderate")
    proxy = result.get("proxy")
    sdUrl = result.get("sdUrl")
    sd1 = result.get("sd审核和反推api")
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
    global UserGet1
    UserGet = {}
    tag_user = {}
    UserGet1 = {}
    
    def parse_arguments(arg_string):
        args = arg_string.split()
        print(f"Split arguments: {args}")  # 调试信息
        result = {}
        for arg in args:
            if arg.startswith('-') and len(arg) > 1:
                # 找到第一个数字的位置
                for i, char in enumerate(arg[1:], start=1):
                    if char.isdigit():
                        break
                else:
                    continue
                
                key = arg[1:i]
                value = arg[i:]
                try:
                    value = int(value)
                except ValueError:
                    print(f"Warning: Invalid value for key '{key}'")  # 调试信息
                    continue
                result[key] = value
            else:
                print(f"Warning: Invalid argument format '{arg}'")  # 调试信息
        return result
    @bot.on(GroupMessage)
    async def bing_dalle3_draw(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            prompt = str(event.message_chain).split("画 ")[1]
            logger.info("发起bing dalle 3 绘画请求，prompt:" + prompt)

            try:
                functions = [
                    #ideo_gram(prompt, proxy),
                    bing_dalle3(prompt, proxy),
                    #flux_speed(prompt, proxy),
                    #recraft_v3(prompt, proxy),
                    flux_ultra(prompt, proxy),
                ]

                for future in asyncio.as_completed(functions):
                    try:
                        result = await future
                        if result:
                            send_list = []
                            for i in result:
                                send_list.append(ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                   message_chain=MessageChain([Image(path=i)])))

                            await bot.send(event, Forward(node_list=send_list))
                    except Exception as e:
                        print(f"Task failed: {e}")

            except Exception as e:
                logger.error(e)
                logger.error("bing dalle 3 Drawer出错")

    @bot.on(GroupMessage)
    async def msDrawer(event: GroupMessage):
        if str(event.message_chain).startswith("画 ") and aiDrawController.get("modelscopeSD"):
            tag = str(event.message_chain).split("画 ")[1]
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
        global turn #画 中空格的意义在于防止误触发，但fluxDrawer无所谓了，其他倒是可以做一做限制。
        global sd_user_args
        if str(event.message_chain).startswith("画 ") and sdUrl!="" and sdUrl!=" ":
            tag = str(event.message_chain).replace("画 ", "")
            path = f"data/pictures/cache/{random_str()}.png"
            logger.info(f"发起SDai绘画请求，path:{path}|prompt:{tag}")
            try:
                await bot.send(event, f'sd前面排队{turn}人，请耐心等待喵~', True)
                turn += 1
                # 没啥好审的，controller直接自个写了。
                args = sd_user_args.get(event.sender.id, {})
                p = await SdDraw0(tag + positive_prompt, negative_prompt, path, sdUrl, event.group.id, args)
                # logger.error(str(p))
                if not p:
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
        
        if str(event.message_chain).startswith("画竖图 ") and sdUrl!="" and sdUrl!=" ":
            tag = str(event.message_chain).replace("画竖图 ", "")
            path = f"data/pictures/cache/{random_str()}.png"
            logger.info(f"发起SDai绘画请求，path:{path}|prompt:{tag}")
            try:
                await bot.send(event, f'开始画竖图啦~sd前面排队{turn}人，请耐心等待喵~', True)
                turn += 1
                # 没啥好审的，controller直接自个写了。
                p = await SdDraw(tag + positive_prompt, negative_prompt, path, sdUrl, event.group.id)
                # logger.error(str(p))
                if not p:
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
                if not p:
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
                if not p:
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
            times = 1
            while times < 8:
                try:
                    logger.info(f"接口1绘画中......第{times}次请求....")
                    p = await draw1(tag, path)
                    logger.error(str(p))
                    await bot.send(event, [Image(path=p[0]), Image(path=p[1]), Image(path=p[2]), Image(path=p[3])],True)                   
                except Exception as e:
                    logger.error(e)
                    logger.error("接口1绘画失败.......")
                    times += 1
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

        if event.message_chain.has(Image) == False and (str(event.message_chain) == "重绘" or str(event.message_chain).startswith("重绘 ")):
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
                args = sd_re_args.get(event.sender.id, {})
                b64_in = await url_to_base64(img_url)
                
                await bot.send(event, f"开始重绘啦~sd前面排队{turn}人，请耐心等待喵~", True)
                turn += 1
                # 将 UserGet[event.sender.id] 列表中的内容和 positive_prompt 合并成一个字符串
                p = await SdreDraw(prompts_str, negative_prompt, path, sdUrl, event.group.id, b64_in, args)
                if not p:
                    turn -= 1
                    logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                else:
                    await bot.send(event, [Image(path=path)], True)
                    turn -= 1
            except Exception as e:
                logger.error(f"重绘失败: {e}")
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
            
    @bot.on(GroupMessage)
    async def tagger(event: GroupMessage):
        global UserGet

        if event.message_chain.has(Image) == False and (str(event.message_chain) == "tag" or str(event.message_chain).startswith("tag ")):
            tag_user[event.sender.id] = []
            await bot.send(event, "请发送要识别的图片")

        # 处理图片和重绘命令
        if (str(event.message_chain).startswith("tag") or event.sender.id in tag_user) and event.message_chain.count(Image):
            if (str(event.message_chain).startswith("tag")) and event.message_chain.count(Image):
                tag_user[event.sender.id] = []

            # 日志记录
            logger.info(f"接收来自群：{event.group.id} 用户：{event.sender.id} 的tag反推指令")

            # 获取图片路径
            path = f"data/pictures/cache/{random_str()}.png"
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            logger.info(f"发起反推tag请求，path:{path}")
            tag_user.pop(event.sender.id)
            
            try:
                b64_in = await url_to_base64(img_url)    
                await bot.send(event, "tag反推中", True)
                message,tags,tags_str = await pic_audit_standalone(b64_in,is_return_tags=True,url =sd1)
                tags_str = tags_str.replace("_"," ")
                await bot.send(event, tags_str, True)
            except Exception as e:
                logger.error(f"反推失败: {e}")
                await bot.send(event, "反推失败了喵~", True)

    async def url_to_base64(url):
        async with httpx.AsyncClient(timeout=9000) as client:
            response = await client.get(url)
            if response.status_code == 200:
                image_bytes = response.content
                encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                return encoded_string
            else:
                raise Exception(f"Failed to retrieve image: {response.status_code}")
    @bot.on(GroupMessage)
    async def sdsettings(event: GroupMessage):
        if str(event.message_chain).startswith("setsd "):
            global sd_user_args
            command = str(event.message_chain).replace("setsd ", "")
            cmd_dict = parse_arguments(command)  # 不需要 await
            sd_user_args[event.sender.id] = cmd_dict
            await bot.send(event, f"当前绘画参数设置: {sd_user_args[event.sender.id]}", True)
    
    @bot.on(GroupMessage)
    async def sdresettings(event: GroupMessage):
        if str(event.message_chain).startswith("setre "):
            global sd_re_args
            command = str(event.message_chain).replace("setre ", "")
            cmd_dict = parse_arguments(command)  # 不需要 await
            sd_re_args[event.sender.id] = cmd_dict
            await bot.send(event, f"当前重绘参数设置: {sd_re_args[event.sender.id]}", True)
            
    @bot.on(GroupMessage)
    async def sdcn1(event: GroupMessage):
        global UserGet1
        global turn

        if event.message_chain.has(Image) == False and (str(event.message_chain) == "cn1" or str(event.message_chain).startswith("cn1 ")):
            prompt = str(event.message_chain).replace("cn1", "").strip()
            UserGet1[event.sender.id] = [prompt]
            await bot.send(event, "请发送要进行cn1预设操作的图片")

        # 处理图片和重绘命令
        if (str(event.message_chain).startswith("cn1") or event.sender.id in UserGet1) and event.message_chain.count(Image):
            if (str(event.message_chain).startswith("cn1")) and event.message_chain.count(Image):
                prompt = str(event.message_chain).replace("cn1", "").strip()
                UserGet1[event.sender.id] = [prompt]

            # 日志记录
            prompts = ', '.join(UserGet1[event.sender.id])
            logger.info(f"接收来自群：{event.group.id} 用户：{event.sender.id} 的cn1指令 prompt: {prompts}")

            # 获取图片路径
            path = f"data/pictures/cache/{random_str()}.png"
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            logger.info(f"发起SDaicn1请求，path:{path}|prompt:{prompts}")
            prompts_str = ' '.join(UserGet1[event.sender.id]) + ' ' + positive_prompt
            UserGet1.pop(event.sender.id)
            

            try:
                args = sd_user_args.get(event.sender.id, {})
                b64_in = await url_to_base64(img_url)
                
                await bot.send(event, f"开始cn1啦~sd前面排队{turn}人，请耐心等待喵~", True)
                turn += 1
                p = await cn1(prompts_str, negative_prompt, path, sdUrl, event.group.id, b64_in, args)
                if not p:
                    turn -= 1
                    logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                else:
                    await bot.send(event, [Image(path=path)], True)
                    turn -= 1
            except Exception as e:
                logger.error(f"cn1失败: {e}")
                await bot.send(event, "cn1失败了喵~", True)

    @bot.on(GroupMessage)
    async def naiDraw4(event: GroupMessage):
        global turn
        global sd_user_args
        if str(event.message_chain).startswith("n4 ") and aiDrawController.get("nai"):
            tag = str(event.message_chain).replace("n4 ", "")
            path = f"data/pictures/cache/{random_str()}.png"
            logger.info(f"发起nai4绘画请求，path:{path}|prompt:{tag}")
            await bot.send(event,'正在进行nai4画图',True)

            async def attempt_draw(retries_left=10): # 这里是递归请求的次数
                try:
                    p = await n4(tag + positive_prompt, negative_prompt, path, event.group.id)
                    if not p:
                        logger.info("色图已屏蔽")
                        await bot.send(event, "杂鱼，色图不给你喵~", True)
                    else:
                        await bot.send(event, [Image(path=path)], True)
                except Exception as e:
                    logger.error(e)
                    if retries_left > 0:
                        logger.error(f"尝试重新请求nai4，剩余尝试次数：{retries_left - 1}")
                        await asyncio.sleep(0.5)  # 等待0.5秒
                        await attempt_draw(retries_left - 1)
                    else:
                        await bot.send(event, "nai只因了，联系master喵~")

            await attempt_draw()

    @bot.on(GroupMessage)
    async def naiDraw3(event: GroupMessage):
        global turn
        global sd_user_args
        if str(event.message_chain).startswith("n3 ") and aiDrawController.get("nai"):
            tag = str(event.message_chain).replace("n3 ", "")
            path = f"data/pictures/cache/{random_str()}.png"
            logger.info(f"发起nai3绘画请求，path:{path}|prompt:{tag}")
            await bot.send(event,'正在进行nai3画图',True)

            async def attempt_draw(retries_left=10): # 这里是递归请求的次数
                try:
                    p = await n3(tag + positive_prompt, negative_prompt, path, event.group.id)
                    if not p:
                        logger.info("色图已屏蔽")
                        await bot.send(event, "杂鱼，色图不给你喵~", True)
                    else:
                        await bot.send(event, [Image(path=path)], True)
                except Exception as e:
                    logger.error(e)
                    if retries_left > 0:
                        logger.error(f"尝试重新请求nai3，剩余尝试次数：{retries_left - 1}")
                        await asyncio.sleep(0.5)  # 等待0.5秒
                        await attempt_draw(retries_left - 1)
                    else:
                        await bot.send(event, "nai只因了，联系master喵~")

            await attempt_draw()    

    @bot.on(GroupMessage)
    async def db(event: GroupMessage):
        if str(event.message_chain).startswith("dan "):
            tag = str(event.message_chain).replace("dan ", "")
            logger.info(f"收到来自群{event.group.id}的请求，prompt:{tag}")
            limit = 3
            proxies = {
                "http://": proxy,
                "https://": proxy,
            }


            db_base_url = "https://kagamihara.donmai.us" #这是反代，原来的是https://danbooru.donmai.us
            #把danbooru换成sonohara、kagamihara、hijiribe这三个任意一个试试，后面的不用改
            

            build_msg = [ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana", message_chain=MessageChain([f"{tag}的搜索结果:"]))]

            msg = tag
            try:
                async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
                    resp = await client.get(
                        f"{db_base_url}/autocomplete?search%5Bquery%5D={msg}&search%5Btype%5D=tag_query&version=1&limit={limit}",
                        follow_redirects=True,
                    )
                    resp.raise_for_status()  # 检查请求是否成功
                    logger.info(f"Autocomplete request successful for tag: {tag}")
            except Exception as e:
                logger.error(f"Failed to get autocomplete data for tag: {tag}. Error: {e}")
                return

            soup = BeautifulSoup(resp.text, 'html.parser')
            tags = soup.find_all('li', class_='ui-menu-item')

            data_values = []
            raw_data_values = []
            for tag in tags:
                data_value = tag['data-autocomplete-value']
                raw_data_values.append(data_value)
                data_value_space = data_value.replace('_', ' ')
                data_values.append(data_value_space)
                logger.info(f"Found autocomplete tag: {data_value_space}")


            for tag in raw_data_values:
                tag1 = tag.replace('_', ' ')
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana", message_chain=MessageChain([f"({tag1}:1)"]))
                build_msg.append(b1)
                formatted_tag = tag.replace(' ', '_').replace('(', '%28').replace(')', '%29')


                try:
                    async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
                        image_resp = await client.get(
                            f"{db_base_url}/posts?tags={formatted_tag}",
                            follow_redirects=True
                        )
                        image_resp.raise_for_status()  # 检查请求是否成功
                        logger.info(f"Posts request successful for tag: {formatted_tag}")
                except Exception as e:
                    logger.error(f"Failed to get posts for tag: {formatted_tag}. Error: {e}")
                    continue  # 继续处理下一个标签

                soup = BeautifulSoup(image_resp.text, 'html.parser')
                img_urls = [img['src'] for img in soup.find_all('img') if img['src'].startswith('http')][:2]
                logger.info(f"Found {len(img_urls)} images for tag: {formatted_tag}")

                async def download_img(image_url: str) -> (str, bytes):
                    try:
                        async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
                            response = await client.get(image_url)
                            response.raise_for_status()
                            content_type = response.headers.get('content-type', '').lower()
                            if not content_type.startswith('image/'):
                                raise ValueError(f"URL {image_url} does not point to an image.")
                            bytes_image = response.content

                            buffered = BytesIO(bytes_image)
                            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                            logger.info(f"Downloaded image from URL: {image_url}")
                            return base64_image, bytes_image

                    except httpx.RequestError as e:
                        logger.error(f"Failed to download image from {image_url}: {e}")
                        raise
                    except Exception as e:
                        logger.error(f"An error occurred while processing the image from {image_url}: {e}")
                        raise

                async def process_image(image_url):
                    try:
                        base64_image, bytes_image = await download_img(image_url)
                        audit_result = await pic_audit_standalone(base64_image, return_none=True, url = sd1)
                        if audit_result:
                            logger.info(f"Image at URL {image_url} was flagged by audit: {audit_result}")
                            return "太涩了"
                        else:
                            logger.info(f"Image at URL {image_url} passed the audit")
                            return Image(url=image_url)
                    except Exception as e:
                        logger.error(f"Failed to process image at {image_url}: {e}")
                        return None

                async def process_images(img_urls):
                    tasks = [process_image(url) for url in img_urls]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # 过滤掉异常和 None 结果
                    filtered_results = [result for result in results if not isinstance(result, Exception) and result is not None]

                    # 创建 ForwardMessageNode 列表
                    forward_messages = [
                        ForwardMessageNode(
                            sender_id=bot.qq,
                            sender_name="Manyana",
                            message_chain=MessageChain([result])
                        )
                        for result in filtered_results
                    ]

                    logger.info(f"Processed {len(filtered_results)} images for tag: {formatted_tag}")
                    return forward_messages

                results = await process_images(img_urls)
                build_msg.extend(results)

            try:
                await bot.send(event, Forward(node_list=build_msg))
                logger.info("Successfully sent the compiled message to the group.")
            except Exception as e:
                logger.error(f"Failed to send the compiled message to the group. Error: {e}")
            
