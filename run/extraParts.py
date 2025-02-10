# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import re
from asyncio import sleep
from io import BytesIO

import httpx
import requests
import yaml
from PIL import Image as Image1
from mirai import GroupMessage, At, Plain
from mirai import Image, Voice, Startup, MessageChain
from mirai.models import ForwardMessageNode, Forward
from mirai.models import MusicShare

from plugins import weatherQuery
from plugins.aiReplyCore import modelReply
from plugins.emojimixhandle import emojimix_handle
from plugins.extraParts import get_cp_mesg, arkOperator, minecraftSeverQuery, eganylist
from plugins.extraParts import hisToday, steamEpic, search_and_download_image
from plugins.gacha import arkGacha, starRailGacha, bbbgacha
from plugins.jokeMaker import get_joke
from plugins.newsEveryDay import news, moyu, xingzuo, sd, chaijun, danxianglii, beCrazy, bingEveryDay
from plugins.picGet import pic, setuGet
from plugins.setuModerate import setuModerate
from plugins.solveSearch import solve
from plugins.tarot import tarotChoice, genshinDraw, qianCao
from plugins.toolkits import random_str, picDwn

_task = None


def main(bot, logger):
    # 读取api列表
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    api_KEY = result.get("weatherXinZhi")
    proxy = result.get("proxy")
    moderateK = result.get("moderate")
    nasa_api = result.get("nasa_api")
    proxy = result.get("proxy")
    proxies = {
        "http://": proxy,
        "https://": proxy
    }

    logger.info("额外的功能 启动完成")
    with open("data/text/odes.json", encoding="utf-8") as fp:
        odes = json.load(fp)
    with open("data/text/IChing.json", encoding="utf-8") as fp:
        IChing = json.load(fp)
    global data
    with open('data/text/nasaTasks.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        data1 = yaml.load(file, Loader=yaml.FullLoader)
    global trustUser
    userdict = data1
    trustUser = []
    for i in userdict.keys():
        data2 = userdict.get(i)
        times = int(str(data2.get('sts')))
        if times > 8:
            trustUser.append(str(i))
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controllerResult = yaml.load(f.read(), Loader=yaml.FullLoader)
    r18 = controllerResult.get("图片相关").get("r18Pic")
    onlyTrustUserR18 = controllerResult.get("图片相关").get("onlyTrustUserR18")
    withPic = controllerResult.get("图片相关").get("withPic")
    watchPrefix = controllerResult.get("图片相关").get("watchPrefix")
    wifePrefix = controllerResult.get("图片相关").get("wifePrefix")
    grayPic = controllerResult.get("图片相关").get("grayPic")
    allowPic = controllerResult.get("图片相关").get("allowPic")
    selfsensor = result1.get("moderate").get("selfsensor")
    selfthreshold = result1.get("moderate").get("selfthreshold")
    aiReplyCore = result1.get("chatGLM").get("aiReplyCore")
    colorfulCharacterList = os.listdir("data/colorfulAnimeCharacter")
    lockResult = controllerResult.get("运势&塔罗").get("lockLuck")
    isAbstract = controllerResult.get("运势&塔罗").get("isAbstract")
    InternetMeme = controllerResult.get("图片相关").get("InternetMeme")

    global picData
    picData = {}
    with open('config/gachaSettings.yaml', 'r', encoding='utf-8') as f:
        resultp = yaml.load(f.read(), Loader=yaml.FullLoader)
    bbb = resultp.get("blueArchiveGacha")
    if lockResult:
        with open('data/lockLuck.yaml', 'r', encoding='utf-8') as f:
            result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
        global luckList
        global tod
        tod = str(datetime.date.today())
        if tod in result2:
            luckList = result2
        else:
            luckList = {str(tod): {"运势": {123: "", 456: ""}, "塔罗": {123: {"text": "hahaha", "path": ",,,"}}}}
            with open('data/lockLuck.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(luckList, file, allow_unicode=True)

    @bot.on(Startup)
    async def update(event: Startup):
        while True:
            await sleep(300)
            logger.info("更新用户数据")
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                data1 = yaml.load(file, Loader=yaml.FullLoader)
            global trustUser
            userdict = data1
            trustUser = []
            for i in userdict.keys():
                data3 = userdict.get(i)
                times = int(str(data3.get('sts')))
                if times > 20:
                    trustUser.append(str(i))

    @bot.on(GroupMessage)
    async def chaijunmaomao(event: GroupMessage):
        if str(event.message_chain) == "柴郡" or (
                At(bot.qq) in event.message_chain and "柴郡" in str(event.message_chain)):
            try:
                logger.info("有楠桐调用了柴郡猫猫图")
                asffd = await chaijun()
                await bot.send(event, Image(path=asffd))
                asffd = await chaijun()
                await bot.send(event, Image(path=asffd))
            except:
                logger.error("获取柴郡.png失败")
                await bot.send(event, "获取失败，请检查网络连接")

    @bot.on(GroupMessage)
    async def fabing(event: GroupMessage):
        if (str(event.message_chain).startswith("发病 ") or (At(bot.qq) in event.message_chain and "发病 " in str(event.message_chain))) and controllerResult.get("小功能").get("发病"):
            try:
                logger.info("开始发病")
                aim = str(event.message_chain).replace(str(At(bot.qq)), "").replace("发病 ", "")
                asffd = await beCrazy(aim)
                logger.info(asffd)
                await bot.send(event, asffd)
            except:
                logger.error("调用接口失败")
                await bot.send(event, "获取失败，请检查网络连接")

    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        # if str(event.message_chain) == '/pic':
        if At(bot.qq) not in event.message_chain:
            if '/pic' in str(event.message_chain):
                picNum = int((str(event.message_chain))[4:])
            elif "@" + str(bot.qq) not in str(event.message_chain) and event.message_chain.count(Image) < 1 and len(
                    str(event.message_chain)) < 6:
                if get_number(str(event.message_chain)) is None:
                    return
                else:
                    picNum = int(get_number(str(event.message_chain)))

            else:
                return
            logger.info("图片获取指令....数量：" + str(picNum))
            if 10 > picNum > -1:
                for i in range(picNum):
                    logger.info("获取壁纸")
                    a = pic()
                    await bot.send(event, Image(path=a))
            elif picNum == '':
                a = pic()
                await bot.send(event, Image(path=a))
            else:
                await bot.send(event, "数字超出限制")
            logger.info("图片获取完成")

    # 整点正则
    pattern = r".*(壁纸|图|pic).*(\d+).*|.*(\d+).*(壁纸|图|pic).*"

    # 定义一个函数，使用正则表达式检查字符串是否符合条件，并提取数字
    def get_number(string):
        # 使用re.match方法，返回匹配的结果对象
        match = re.match(pattern, string)
        # 如果结果对象不为空，返回捕获的数字，否则返回None
        if match:
            # 如果第二个分组有值，返回第二个分组，否则返回第三个分组
            if match.group(2):
                return match.group(2)
            else:
                return match.group(3)
        else:
            return None

    @bot.on(GroupMessage)
    async def setuHelper(event: GroupMessage):
        pattern1 = r'(\d+)张(\w+)'
        global picData
        if At(bot.qq) in event.message_chain:
            text1 = str(event.message_chain).replace("壁纸", "").replace("涩图", "").replace("色图", "").replace("图",
                                                                                                                 "").replace(
                "r18", "")
            match1 = re.search(pattern1, text1)
            if match1:
                if not allowPic:
                    await bot.send(event, "发图功能已关闭，可使用 5图 指令使用备用发图功能")
                    return
                logger.info("提取图片关键字。 数量: " + str(match1.group(1)) + " 关键字: " + match1.group(2))
                data = {"tag": ""}
                if "r18" in str(event.message_chain) or "色图" in str(event.message_chain) or "涩图" in str(
                        event.message_chain):
                    if (str(event.sender.id) in trustUser and onlyTrustUserR18) or r18:
                        data["r18"] = 1
                    else:
                        await bot.send(event, "r18模式已关闭")
                picData[event.sender.id] = []
                data["tag"] = match1.group(2)
                data["size"] = "regular"
                logger.info("组装数据完成：" + str(data))
                a = int(match1.group(1))
                if int(match1.group(1)) > 6:
                    a = 5
                    await bot.send(event, "api访问限制，修改获取张数为 5")
                fordMes = []
                for i in range(a):
                    try:
                        url, path = await setuGet(data, withPic, grayPic)
                    except Exception as e:
                        logger.error(e)
                        logger.error("涩图请求出错")
                        # await bot.send(event,"请求出错，请稍后再试")
                        continue
                    logger.info(f"获取到图片: {url} {path}")

                    if selfsensor:
                        try:
                            thurs = await setuModerate(url, moderateK)
                            logger.info(f"获取到审核结果： adult- {thurs}")
                            if int(thurs) > selfthreshold:
                                logger.warning(f"不安全的图片，自我审核过滤")
                                await bot.send(event, ["nsfw内容已过滤", Image(
                                    path="data/colorfulAnimeCharacter/" + random.choice(
                                        os.listdir("data/colorfulAnimeCharacter")))])
                                continue
                        except Exception as e:
                            logger.error(e)
                            logger.error("无法进行自我审核，错误的网络环境或apikey")
                            await bot.send(event, ["审核策略失效，为确保安全，不显示本图片", Image(
                                path="data/colorfulAnimeCharacter/" + random.choice(
                                    os.listdir("data/colorfulAnimeCharacter")))])
                            continue
                    if withPic:
                        b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([url, Image(path=path)]))
                    else:
                        b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([url]))
                    fordMes.append(b1)
                    # await bot.send(event, Image(url=path))
                    logger.info("图片获取成功")
                try:
                    await bot.send(event, Forward(node_list=fordMes))

                except Exception as e:
                    logger.error(e)
                    await bot.send(event, "出错，请稍后再试")

    @bot.on(GroupMessage)
    async def emojiMix(event: GroupMessage):
        if len(str(event.message_chain)) == 2:
            r = list(str(event.message_chain))
            try:
                p = await emojimix_handle(r[0], r[1])
            except:
                return
            #            if p!=None:
            #                logger.info(f"emoji合成：{r[0]} + {r[1]}")
            #                await bot.send(event,Image(path=p),True)
            if p == "not_emoji":
                return
            elif p == 'a':
                msg = f'不正确的参数：{r[0]}'
            elif p == 'b':
                msg = f'不正确的参数：{r[1]}'
            elif p is None:
                msg = '表情不支持，请重新选择'
            else:
                logger.info(f"emoji合成：{r[0]} + {r[1]}")
                if p.startswith('https://'):
                    png_path = "data/pictures/cache/" + random_str() + ".png"
                    async with httpx.AsyncClient(timeout=20) as client:
                        r = await client.get(p)
                        with open(png_path, "wb") as f:
                            f.write(r.content)  # 从二进制数据创建图片对象
                    # msg = MessageSegment.image(result)
                    await bot.send(event, Image(path=png_path), True)
                else:
                    await bot.send(event, Image(path=p), True)
                    # msg = MessageSegment.image('file://'+result)
            # await emojimix.send(msg)

    @bot.on(GroupMessage)
    async def historyToday(event: GroupMessage):
        pattern = r".*历史.*今天.*|.*今天.*历史.*"
        string = str(event.message_chain)
        match = re.search(pattern, string)
        if match:
            dataBack = await hisToday()
            logger.info("获取历史上的今天")
            logger.info(str(dataBack))
            sendData = str(dataBack.get("result")).replace("[", " ").replace("{'year': '", "").replace("'}",
                                                                                                       "").replace("]",
                                                                                                                   "").replace(
                "', 'title': '", " ").replace(",", "\n")
            await bot.send(event, sendData)

    @bot.on(GroupMessage)
    async def weather_query(event: GroupMessage):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^查询\s*(\w+)\s*$', msg.strip())
        if m:
            # 取出指令中的地名
            city = m.group(1)
            logger.info("查询 " + city + " 天气")
            await bot.send(event, '查询中……')
            # 发送天气消息
            if aiReplyCore:
                wSult = await weatherQuery.fullQuery(city)
                r = await modelReply(event.sender.member_name, event.sender.id,
                                     f"请你为我进行天气播报，下面是天气查询的结果：{wSult}")
                await bot.send(event, r, True)
            else:
                wSult = await weatherQuery.querys(city, api_KEY)
                await bot.send(event, wSult, True)

    @bot.on(GroupMessage)
    async def newsToday(event: GroupMessage):
        if ("新闻" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "新闻":
            logger.info("获取新闻")
            path = await news()
            logger.info("成功获取到今日新闻")
            await bot.send(event, Image(path=path))

    @bot.on(GroupMessage)
    async def searchpic(event: GroupMessage):
        if str(event.message_chain).startswith(f"{watchPrefix}看看") or str(event.message_chain).startswith(
                f"{watchPrefix}搜索"):
            text = str(event.message_chain)
            text = text.replace(f"{watchPrefix}看看", "").replace(f"{watchPrefix}搜索", "")

            try:
                baidupath = await search_and_download_image(text)
                logger.info("搜索图片开始" + text)
                await bot.send(event, Image(path=baidupath))
                os.remove(baidupath)
            except:
                logger.error("搜索图片错误")
                # await bot.send_group_message(event.group_id, [Text("获取失败，请检查网络连接"),

    @bot.on(GroupMessage)
    async def onedimensionli(event: GroupMessage):
        if ("单向历" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "单向历":
            logger.info("获取单向历")
            path = await danxianglii()
            logger.info("成功获取到单向历")
            await bot.send(event, Image(path=path))

    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("摸鱼" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "摸鱼":
            logger.info("获取摸鱼人日历")
            path = await moyu()
            logger.info("成功获取到摸鱼人日历")
            await bot.send(event, Image(path=path))

    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("星座" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "星座":
            logger.info("获取星座运势")
            path = await xingzuo()
            logger.info("成功获取到星座运势")
            await bot.send(event, Image(path=path))

    @bot.on(GroupMessage)
    async def make_jokes(event: GroupMessage):
        if str(event.message_chain).startswith('/') and str(event.message_chain).endswith('笑话'):
            x = str(event.message_chain).strip()[1:-2]
            joke = get_joke(x)
            await bot.send(event, joke)

    # 凑个cp
    @bot.on(GroupMessage)
    async def make_cp_mesg(event: GroupMessage):
        if str(event.message_chain).startswith("/cp "):
            x = str(event.message_chain).replace('/cp ', '', 1)
            x = x.split(' ')
            if len(x) != 2:
                await bot.send(event, 'エラーが発生しました。再入力してください')
                return
            mesg = get_cp_mesg(x[0], x[1])
            await bot.send(event, mesg, True)

    @bot.on(GroupMessage)
    async def NasaHelper(event: GroupMessage):
        global data
        if At(bot.qq) in event.message_chain and "天文" in str(event.message_chain):
            # logger.info(str(data.keys()))
            if datetime.datetime.now().strftime('%Y-%m-%d') in data.keys():
                todayNasa = data.get(datetime.datetime.now().strftime('%Y-%m-%d'))
                path = todayNasa.get("path")
                txt = todayNasa.get("transTxt")
                try:
                    await bot.send(event, (Image(path=path), txt))
                except:
                    await bot.send(event, txt)
            else:
                proxies = {
                    "http://": proxy,
                    "https://": proxy
                }
                # Replace the key with your own
                dataa = {"api_key": nasa_api}
                logger.info("发起nasa请求")
                try:
                    # 拼接url和参数
                    url = "https://api.nasa.gov/planetary/apod?" + "&".join([f"{k}={v}" for k, v in dataa.items()])
                    async with httpx.AsyncClient(proxies=proxies) as client:
                        # 用get方法发送请求
                        response = await client.get(url=url)
                    # response = requests.post(url="https://saucenao.com/search.php", data=dataa, proxies=proxies)
                    logger.info("获取到结果" + str(response.json()))
                    # logger.info("下载缩略图")
                    filename = await picDwn(response.json().get("url"),
                                            "data/pictures/nasa/" + response.json().get("date") + ".png")

                    txt = response.json().get("date") + "\n" + response.json().get(
                        "title") + "\n" + response.json().get("explanation")
                    if aiReplyCore:
                        txt = await modelReply(event.sender.member_name, event.sender.id,
                                               f"将下面这段内容翻译为中文:{txt}")
                    temp = {"path": "data/pictures/nasa/" + response.json().get("date") + ".png",
                            "oriTxt": response.json().get("explanation"), "transTxt": txt}

                    data[datetime.datetime.now().strftime('%Y-%m-%d')] = temp

                    with open('data/text/nasaTasks.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(data, file, allow_unicode=True)

                    await bot.send(event, (Image(path=filename), txt))

                except:
                    logger.warning("获取每日天文图片失败")
                    await bot.send(event, "获取失败，请联系master检查代理或api_key是否可用")

    @bot.on(GroupMessage)
    async def arkGene(event: GroupMessage):
        if "干员" in str(event.message_chain) and "生成" in str(event.message_chain):
            logger.info("又有皱皮了，生成干员信息中.....")
            o = arkOperator()
            o = o.replace("为生成", event.sender.member_name)
            await bot.send(event, o, True)

    @bot.on(GroupMessage)
    async def genshin1(event: GroupMessage):
        if ("原神" in str(event.message_chain) and "启动" in str(event.message_chain)) or (
                "抽签" in str(event.message_chain) and "原" in str(event.message_chain)):
            logger.info("有原皮！获取抽签信息中....")
            o = genshinDraw()
            logger.info("\n" + o)
            await bot.send(event, o, True)

    @bot.on(GroupMessage)
    async def genshin1(event: GroupMessage):
        if ("抽签" in str(event.message_chain) and At(bot.qq) in event.message_chain) or "抽签" == str(
                event.message_chain):
            logger.info("获取浅草百签")
            o = qianCao()
            logger.info(o)
            await bot.send(event, o, True)
            if aiReplyCore:
                r = await modelReply(event.sender.member_name, event.sender.id, f"为我进行解签，下面是抽签的结果:{o}")
                await bot.send(event, r, True)

    @bot.on(GroupMessage)
    async def NasaHelper(event: GroupMessage):
        if At(bot.qq) in event.message_chain and "诗经" in str(event.message_chain):
            logger.info("获取一篇诗经")
            ode = random.choice(odes.get("诗经"))
            logger.info("\n" + ode)
            await bot.send(event, ode)
            if aiReplyCore:
                r = await modelReply(event.sender.member_name, event.sender.id,
                                     f"下面这首诗来自《诗经》，为我介绍它:{ode}")
                await bot.send(event, r, True)

    @bot.on(GroupMessage)
    async def NasaHelper(event: GroupMessage):
        if At(bot.qq) in event.message_chain and "周易" in str(event.message_chain):
            logger.info("获取卦象")
            IChing1 = random.choice(IChing.get("六十四卦"))
            logger.info("\n" + IChing1)
            await bot.send(event, IChing1)

    @bot.on(GroupMessage)
    async def handwrite(event: GroupMessage):
        if str(event.message_chain).startswith("手写 "):
            msg = str(event.message_chain).replace("手写 ", "")
            logger.info("手写模拟:" + msg)
            try:
                path = await handwrite(msg)
                await bot.send(event, Image(path=path), True)
            except:
                logger.error("调用手写模拟器失败")

    @bot.on(GroupMessage)
    async def jiangzhuang(event: GroupMessage):
        if str(event.message_chain).startswith("/奖状") or str(event.message_chain).startswith("/证书"):
            try:
                t = str(event.message_chain)[3:].split("#")
                if str(event.message_chain).startswith("/奖状"):
                    url = "https://api.pearktrue.cn/api/certcommend/?name=" + t[0] + "&title=" + t[1] + "&classname=" + \
                          t[2]
                else:
                    url = "https://api.pearktrue.cn/api/certificate/?name=" + t[0] + "&title=" + t[1] + "&text=" + t[2]
                p = await sd(url, "data/pictures/cache/" + random_str() + ".png")
                await bot.send(event, Image(path=p))
            except:
                await bot.send(event, "出错\n格式请按照/奖状 name#title#text\n例子\n/奖状 牢大#耐摔王#康师傅冰红茶")

    @bot.on(GroupMessage)
    async def jiangzhuang(event: GroupMessage):
        if str(event.message_chain).startswith("/ba ") and "#" in str(event.message_chain):
            try:
                t = str(event.message_chain).replace("/ba ", "").split("#")
                url = "https://oiapi.net/API/BlueArchive?startText=" + t[0] + "&endText=" + t[1]

                p = await sd(url, "data/pictures/cache/" + random_str() + ".png")
                await bot.send(event, Image(path=p))
            except:
                await bot.send(event, "出错，格式请按照/ba Blue#Archive")
    @bot.on(GroupMessage)
    async def bingToday(event: GroupMessage):
        if str(event.message_chain)=="今日bing" or str(event.message_chain)=="今日必应":
            text,p=await bingEveryDay()
            await bot.send(event,[text,Image(path=p)])
    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("方舟十连" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "方舟十连":
            logger.info("获取方舟抽卡结果")
            try:
                path = await arkGacha()
                logger.info("成功获取到抽卡结果")
                await bot.send(event, Image(path=path), True)
            except:
                logger.error("皱皮衮")
                await bot.send(event, "获取抽卡结果失败，请稍后再试")

    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("星铁十连" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "星铁十连":
            logger.info("获取星铁抽卡结果")
            try:
                path = await starRailGacha()
                logger.info("成功获取到星铁抽卡结果")
                await bot.send(event, Image(path=path), True)
            except:
                logger.error("穹批衮")
                await bot.send(event, "获取抽卡结果失败，请稍后再试")

    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("ba十连" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "ba十连":
            logger.info("获取ba抽卡结果")
            try:
                path = await bbbgacha(bbb)
                logger.info("成功获取到ba抽卡结果")
                await bot.send(event, Image(path=path), True)
            except:
                logger.error("碧批衮")
                await bot.send(event, "获取抽卡结果失败，请稍后再试")

    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("喜加一" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "喜加一":
            logger.info("获取喜加一结果")
            try:
                path = await steamEpic()
                logger.info("获取喜加一结果")
                await bot.send(event, path, True)
            except:
                logger.error("衮")
                await bot.send(event, "获取喜加一结果失败，请稍后再试")

    @bot.on(GroupMessage)
    async def tail(event: GroupMessage):
        if str(event.message_chain).startswith("小尾巴 "):
            tail = str(event.message_chain).replace("小尾巴", "")
            url = f"https://www.oexan.cn/API/ncwb.php?name=后缀：&wb={tail}"
            async with httpx.AsyncClient(timeout=40) as client:
                r1 = await client.get(url)
            await bot.send(event, "请完整复制如下内容，否则无法使用", True)
            await bot.send(event, r1.text.replace("后缀：", ""))

    @bot.on(GroupMessage)
    async def zhifubao(event: GroupMessage):
        if str(event.message_chain).startswith("支付宝到账 "):
            try:
                numb = str(event.message_chain).replace("支付宝到账 ", "")
                url = f"https://free.wqwlkj.cn/wqwlapi/alipay_yy.php?money={str(numb)}"
                r = requests.get(url)
                p = "data/voices/" + random_str() + '.wav'
                logger.info(f"支付宝到账：{numb}")
                with open(p, "wb") as f:
                    f.write(r.content)
                await bot.send(event, Voice(path=p))
            except Exception as e:
                logger.error(e)
                await bot.send(event, "生成失败，请检查数额")

    @bot.on(GroupMessage)
    async def meme(event: GroupMessage):
        global memeData
        if str(event.message_chain) == "meme" or (
                "meme" in str(event.message_chain) and At(bot.qq) in event.message_chain):
            if InternetMeme:
                logger.info("使用网络meme")

                url = 'https://meme-api.com/gimme'
                proxies = {
                    "http://": proxy,
                    "https://": proxy
                }
                async with httpx.AsyncClient(timeout=20) as client:
                    r = await client.get(url)
                    logger.info(r.json().get("preview")[-1])
                    async with httpx.AsyncClient(timeout=20, proxies=proxies) as client:
                        r = await client.get(r.json().get("preview")[-1])
                        img = Image1.open(BytesIO(r.content))  # 从二进制数据创建图片对象
                        path = "data/pictures/meme/" + random_str() + ".png"
                        img.save(path)  # 使用PIL库保存图片
                        await bot.send(event, Image(path=path))

            else:
                logger.warning("使用本地meme图")
                la = os.listdir("data/pictures/meme")
                la = "data/pictures/meme/" + random.choice(la)
                logger.info("掉落了一张meme图")
                await bot.send(event, (str(event.sender.member_name) + "得到了一张meme图", Image(path=la)))

    @bot.on(GroupMessage)
    async def meme(event: GroupMessage):
        global memeData, luckList, tod
        if ("运势" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "运势":
            if not lockResult:
                la = os.listdir("data/pictures/amm")
                la = "data/pictures/amm/" + random.choice(la)
                logger.info("执行运势查询")
                await bot.send(event, (str(event.sender.member_name) + "今天的运势是", Image(path=la)))
            else:
                if event.sender.id not in luckList.get(str(tod)).get("运势"):
                    la = os.listdir("data/pictures/amm")
                    la = "data/pictures/amm/" + random.choice(la)
                    logger.info("执行运势查询")
                    await bot.send(event, (str(event.sender.member_name) + "今天的运势是", Image(path=la)))
                    luckList[str(tod)]["运势"][event.sender.id] = la
                else:
                    la = luckList.get(str(tod)).get("运势").get(event.sender.id)
                    logger.info("执行运势查询")
                    await bot.send(event, (str(event.sender.member_name) + "今天的运势是", Image(path=la)))
                with open('data/lockLuck.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(luckList, file, allow_unicode=True)

    @bot.on(GroupMessage)
    async def tarotToday(event: GroupMessage):
        global luckList, tod
        if ("今日塔罗" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "今日塔罗":
            logger.info("获取今日塔罗")
            if not lockResult:
                txt, img = tarotChoice(isAbstract)
                logger.info("成功获取到今日塔罗")
                try:
                    if isAbstract:
                        if "力量 (Strength)" in txt:
                            await bot.send(event, Voice(
                                url="https://m801.music.126.net/20240927102917/f92d9dfa857ef3dac3d7bfc9ffbaf494/jdymusic/obj/wo3DlMOGwrbDjj7DisKw/35734009350/2121/0e15/81af/13353efc7a486802928c8cf612e31b78.mp3"))
                except Exception as e:
                    logger.error(e)
                await bot.send(event, [txt, Image(path=img)])
                if aiReplyCore:
                    r = await modelReply(event.sender.member_name, event.sender.id,
                                         f"为我进行塔罗牌播报，下面是塔罗占卜的结果{txt}")
                    await bot.send(event, r, True)

            else:
                if event.sender.id not in luckList.get(tod).get("塔罗"):
                    txt, img = tarotChoice(isAbstract)
                    logger.info("成功获取到今日塔罗")
                    await bot.send(event, txt)
                    await bot.send(event, Image(path=img))
                    luckList[str(tod)]["塔罗"][event.sender.id] = {"text": txt, "img": img}
                else:
                    la = luckList.get(str(tod)).get("塔罗").get(event.sender.id)
                    logger.info("获取塔罗")

                    await bot.send(event, la.get("text"))
                    await bot.send(event, Image(path=la.get("img")))
                if aiReplyCore:
                    r = await modelReply(event.sender.member_name, event.sender.id,
                                         f"为我进行塔罗牌播报，下面是塔罗占卜的结果:{txt}")
                    await bot.send(event, r, True)
                with open('data/lockLuck.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(luckList, file, allow_unicode=True)

    @bot.on(GroupMessage)
    async def tarotToday(event: GroupMessage):
        if ("彩色小人" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "彩色小人":
            logger.info("彩色小人，启动！")
            c = random.choice(colorfulCharacterList)
            await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))

    @bot.on(GroupMessage)
    async def tarotToday(event: GroupMessage):
        if str(event.message_chain).startswith("查在线"):
            try:
                ip = str(event.message_chain).replace("查在线", "")
                logger.info(f"查mc服务器{ip}")
                a, b, c = await minecraftSeverQuery(ip)
                await bot.send(event, [Image(url=a), b, c], True)
            except Exception as e:
                logger.error(e)
                logger.error("mc服务器查询失败")
                await bot.send(event, "查询失败，请检查网络连接", True)

    @bot.on(GroupMessage)
    async def tarotToday(event: GroupMessage):
        if str(event.message_chain).startswith("语法分析"):
            try:
                text = str(event.message_chain).replace("语法分析", "")
                logger.info(f"语法分析{text}")
                p = await eganylist(text, proxy)
                await bot.send(event, Image(path=p), True)
            except Exception as e:
                logger.error(e)
                logger.error("语法分析结果查询失败")
                await bot.send(event, "查询失败，请检查网络连接", True)

    @bot.on(Startup)
    async def updateData(event: Startup):
        while True:
            await sleep(60)
            if lockResult:
                with open('data/lockLuck.yaml', 'r', encoding='utf-8') as f:
                    result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
                global luckList, tod
                tod = str(datetime.date.today())
                if tod in result2:
                    luckList = result2
                else:
                    luckList = {
                        str(tod): {"运势": {123: "", 456: ""}, "塔罗": {123: {"text": "hahaha", "path": ",,,"}}}}
                    with open('data/lockLuck.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(luckList, file, allow_unicode=True)

    @bot.on(GroupMessage)
    async def searchGame(event: GroupMessage):
        if str(event.message_chain).startswith("steam查询"):
            keyword = str(event.message_chain).replace("steam查询", "")
            try:
                logger.info(f"查询游戏{keyword}")
                result_dict = await solve(keyword)
                if result_dict is None:
                    await bot.send(event, "没有找到哦，试试其他名字~")
                    return
                logger.info(result_dict)
                text = "游戏："
                text = text + result_dict['name'] + f"({result_dict['name_cn']})" + "\n游戏id：" + str(result_dict[
                                                                                                          'app_id']) + "\n游戏描述：" + f"{result_dict['description']}\nSteamUrl：" + f"{result_dict['steam_url']}"
                await bot.send(event, (Image(path=result_dict['path']), text))
            except Exception as e:
                logger.error(e)
                logger.exception("详细错误如下：")
                await bot.send(event, "查询失败")

    @bot.on(GroupMessage)
    async def randomASMR(event: GroupMessage):
        if ("随机奥术" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "随机奥术":
            from plugins.youtube0 import ASMR_random, get_audio, get_img
            logger.info("奥术魔刃，启动！")
            athor, title, video_id, length = await ASMR_random()
            imgurl = await get_img(video_id)
            audiourl = await get_audio(video_id)

            st1 = "标题:" + title + "\n"
            st1 += "频道：" + athor + "\n"
            st1 += f"时长：{length // 60}分{length % 60}秒\n"
            await bot.send(event, [st1, Image(url=imgurl)])
            await bot.send(event, MusicShare(kind="QQMusic",
                                             title=title,
                                             summary=athor,
                                             jump_url=f"https://www.amoyshare.com/player/?v={video_id}",
                                             picture_url=imgurl,
                                             music_url=audiourl,
                                             brief='ASMR'))



