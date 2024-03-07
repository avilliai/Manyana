# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import re
import time
import sys
import socket
from asyncio import sleep

import httpx
import requests
import utils
import yaml
from mirai import Image, Voice, Startup, MessageChain
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import ForwardMessageNode, Forward, App

from plugins import weatherQuery
from plugins.RandomStr import random_str
from plugins.arkOperator import arkOperator
from plugins.cpGenerate import get_cp_mesg
from plugins.gacha import arkGacha, starRailGacha, bbbgacha
from plugins.genshinGo import genshinDraw, qianCao
from plugins.historicalToday import hisToday, steamEpic
from plugins.imgDownload import dict_download_img
from plugins.jokeMaker import get_joke

from plugins.modelsLoader import modelLoader
from plugins.newLogger import newLogger
from plugins.newsEveryDay import news, moyu, xingzuo, sd, chaijun, danxianglii
from plugins.arksign import arkSign
from plugins.picGet import pic, setuGet, picDwn
from plugins.tarot import tarotChoice
from plugins.translater import translate

from plugins.webScreenShoot import webScreenShoot, screenshot_to_pdf_and_png


def main(bot,api_KEY,nasa_api,proxy,logger):
    logger.info("额外的功能 启动完成")
    with open("data/odes.json",encoding="utf-8") as fp:
        odes=json.loads(fp.read())
    with open("data/IChing.json",encoding="utf-8") as fp:
        IChing=json.loads(fp.read())
    global data
    with open('data/nasaTasks.yaml', 'r',encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    with open('data/userData.yaml', 'r',encoding='utf-8') as file:
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
    r18 = result1.get("r18Pic")
    global picData
    picData={}
    with open('config/gachaSettings.yaml', 'r', encoding='utf-8') as f:
        resultp = yaml.load(f.read(), Loader=yaml.FullLoader)
    bbb = resultp.get("blueArchiveGacha")
    @bot.on(Startup)
    async def update(event:Startup):
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
        if str(event.message_chain)=="柴郡" or (At(bot.qq) in event.message_chain and "柴郡" in str(event.message_chain)):
            logger.info("有楠桐调用了柴郡猫猫图")
            asffd=await chaijun()
            await bot.send(event,Image(path=asffd))
    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        # if str(event.message_chain) == '/pic':
        if At(bot.qq) not in event.message_chain:
            if '/pic' in str(event.message_chain):
                picNum = int((str(event.message_chain))[4:])
            elif "@"+str(bot.qq) not in str(event.message_chain) and event.message_chain.count(Image)<1 and len(str(event.message_chain))<6:
                if get_number(str(event.message_chain))==None:
                    return
                else:
                    picNum=int(get_number(str(event.message_chain)))

            else:
                return
            logger.info("图片获取指令....数量："+str(picNum))
            if picNum < 10 and picNum > -1:
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
    async def setuHelper(event:GroupMessage):
        pattern1 = r'(\d+)张(\w+)'
        global picData
        if At(bot.qq) in event.message_chain:
            text1=str(event.message_chain).replace("壁纸","").replace("涩图","").replace("色图","").replace("图","").replace("r18","")
            match1 = re.search(pattern1, text1)
            if match1:
                logger.info("提取图片关键字。 数量: "+str(match1.group(1))+" 关键字: "+match1.group(2))
                data={"tag":""}
                if "r18" in str(event.message_chain) or "色图" in str(event.message_chain) or "涩图" in str(event.message_chain):
                    if str(event.sender.id) in trustUser and r18==True :
                        data["r18"]=1
                    else:
                        await bot.send(event,"r18模式已关闭")
                picData[event.sender.id]=[]
                data["tag"]=match1.group(2)
                data["size"] = "regular"
                logger.info("组装数据完成："+str(data))
                a=int(match1.group(1))
                if int(match1.group(1))>6:
                    a=5
                    await bot.send(event,"api访问限制，修改获取张数为 5")
                for i in range(a):
                    try:
                        path=await setuGet(data)
                    except:
                        logger.error("涩图请求出错")
                        await bot.send(event,"请求出错，请稍后再试")
                        return
                    logger.info("发送图片: "+path)
                    try:
                        try:
                            card=await arkSign(path)
                            await bot.send(event,App(card))
                        except Exception as e:
                            logger.error(e)
                            logger.error("自动转换卡片失败")
                        await bot.send(event, Image(url=path))
                        logger.info("图片发送成功")
                    except:
                        logger.error("图片发送失败")
                        await bot.send(event,path)
                    '''try:
                        b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([" " , Image(url=path)]))
                        picData.get(event.sender.id).append(b1)
                    except:
                        logger.error("出错，转为url文本")
                        b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([" " , path]))
                        picData.get(event.sender.id).append(b1)
                    
                await bot.send(event, Forward(node_list=picData.get(event.sender.id)))
                picData.pop(event.sender.id)'''


    @bot.on(GroupMessage)
    async def historyToday(event:GroupMessage):
        pattern = r".*史.*今.*|.*今.*史.*"
        string = str(event.message_chain)
        match = re.search(pattern, string)
        if match:
            dataBack=await hisToday()
            logger.info("获取历史上的今天")
            logger.info(str(dataBack))
            sendData=str(dataBack.get("result")).replace("["," ").replace("{'year': '","").replace("'}","").replace("]","").replace("', 'title': '"," ").replace(",","\n")
            await bot.send(event,sendData)

    @bot.on(GroupMessage)
    async def weather_query(event: GroupMessage):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^查询\s*(\w+)\s*$', msg.strip())
        if m:
            # 取出指令中的地名
            city = m.group(1)
            logger.info("查询 "+city+" 天气")
            await bot.send(event, '查询中……')
            # 发送天气消息
            await bot.send(event, await weatherQuery.querys(city,api_KEY))
    @bot.on(GroupMessage)
    async def newsToday(event:GroupMessage):
        if ("新闻" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain)=="新闻":
            logger.info("获取新闻")
            path=await news()
            logger.info("成功获取到今日新闻")
            await bot.send(event,Image(path=path))
    @bot.on(GroupMessage)
    async def onedimensionli(event:GroupMessage):
        if ("单向历" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain)=="单向历":
            logger.info("获取单向历")
            path=await danxianglii()
            logger.info("成功获取到单向历")
            await bot.send(event,Image(path=path))
    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("摸鱼" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain)=="摸鱼":
            logger.info("获取摸鱼人日历")
            path = await moyu()
            logger.info("成功获取到摸鱼人日历")
            await bot.send(event, Image(path=path))

    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("星座" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain) == "星座":
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
            #logger.info(str(data.keys()))
            if datetime.datetime.now().strftime('%Y-%m-%d') in data.keys():
                todayNasa=data.get(datetime.datetime.now().strftime('%Y-%m-%d'))
                path=todayNasa.get("path")
                txt=todayNasa.get("transTxt")
                try:
                    await bot.send(event, (Image(path=path), txt))
                except:
                    await bot.send(event,txt)
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
                    filename = await picDwn(response.json().get("url"), "data/pictures/nasa/"+response.json().get("date")+".png")
                    txta=await translate(response.json().get("explanation"),mode="EN2ZH_CN")
                    txt = response.json().get("date") + "\n" + response.json().get("title") + "\n" + txta
                    temp={"path":"data/pictures/nasa/"+response.json().get("date")+".png","oriTxt":response.json().get("explanation"),"transTxt":txt}

                    data[datetime.datetime.now().strftime('%Y-%m-%d')]=temp

                    with open('data/nasaTasks.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(data, file, allow_unicode=True)
                    await bot.send(event,(Image(path=filename),txt))

                except:
                    logger.warning("获取每日天文图片失败")
                    await bot.send(event,"获取失败，请联系master检查代理或api_key是否可用")
    @bot.on(GroupMessage)
    async def arkGene(event:GroupMessage):
        if "干员" in str(event.message_chain) and "生成" in str(event.message_chain):
            logger.info("又有皱皮了，生成干员信息中.....")
            o=arkOperator()
            o=o.replace("为生成",event.sender.member_name)
            await bot.send(event,o,True)

    @bot.on(GroupMessage)
    async def genshin1(event: GroupMessage):
        if ("原神" in str(event.message_chain) and "启动" in str(event.message_chain)) or ("抽签" in str(event.message_chain) and "原" in str(event.message_chain)):
            logger.info("有原皮！获取抽签信息中....")
            o = genshinDraw()
            logger.info("\n"+o)
            await bot.send(event, o, True)

    @bot.on(GroupMessage)
    async def genshin1(event: GroupMessage):
        if ("抽签" in str(event.message_chain) and At(bot.qq) in event.message_chain) or "抽签"==str(event.message_chain):
            logger.info("获取浅草百签")
            o = qianCao()
            logger.info(o)
            await bot.send(event, o, True)
    @bot.on(GroupMessage)
    async def NasaHelper(event: GroupMessage):
        if At(bot.qq) in event.message_chain and "诗经" in str(event.message_chain):
            logger.info("获取一篇诗经")
            ode=random.choice(odes.get("诗经"))
            logger.info("\n"+ode)
            await bot.send(event,ode)

    @bot.on(GroupMessage)
    async def NasaHelper(event: GroupMessage):
        if At(bot.qq) in event.message_chain and "周易" in str(event.message_chain):
            logger.info("获取卦象")
            IChing1 = random.choice(IChing.get("六十四卦"))
            logger.info("\n" + IChing1)
            await bot.send(event, IChing1)

    @bot.on(GroupMessage)
    async def screenShoot(event: GroupMessage):
        if str(event.message_chain).startswith("截图#"):
            url=str(event.message_chain).split("#")[1]
            path="data/pictures/cache/"+random_str()+".png"
            logger.info("接收网页截图任务url:"+url)
            try:
                await screenshot_to_pdf_and_png(url, path)
            except:
                logger.error("截图失败!")
            await bot.send(event, Image(path=path), True)

    @bot.on(GroupMessage)
    async def NasaHelper(event: GroupMessage):
        if str(event.message_chain).startswith("/sd"):
            try:

                ls=str(event.message_chain)[3:]
            except:
                await bot.send("未传递合法的prompt")
                return
            logger.info("拆分获取prompt:"+str(ls))
            try:
                url = "https://api.pearktrue.cn/api/stablediffusion/?prompt=" + str(ls) + "&model=normal"
                url=requests.get(url).json().get("imgurl")
            except:
                logger.error("出错")
                await bot.send(event, "出错，请稍后再试")
                return 
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                p=await sd(url,path)
            except:
                logger.error("出错")
                await bot.send(event,"出错，请稍后再试")
                return
            await bot.send(event, Image(path=p),True)
    @bot.on(GroupMessage)
    async def jiangzhuang(event:GroupMessage):
        if str(event.message_chain).startswith("/奖状") or str(event.message_chain).startswith("/证书"):
            try:
                t=str(event.message_chain)[3:].split("#")
                if str(event.message_chain).startswith("/奖状"):
                    url="https://api.pearktrue.cn/api/certcommend/?name="+t[0]+"&title="+t[1]+"&classname="+t[2]
                else:
                    url="https://api.pearktrue.cn/api/certificate/?name="+t[0]+"&title="+t[1]+"&text="+t[2]
                p=await sd(url,"data/pictures/cache/"+random_str()+".png")
                await bot.send(event,Image(path=p))
            except:
                await bot.send(event,"出错，格式请按照/奖状(或证书) name#title#text")

    @bot.on(GroupMessage)
    async def jiangzhuang(event:GroupMessage):
        if str(event.message_chain).startswith("/ba ") and "#" in str(event.message_chain):
            try:
                t=str(event.message_chain).replace("/ba ","").split("#")
                url="https://oiapi.net/API/BlueArchive?startText="+t[0]+"&endText="+t[1]

                p=await sd(url,"data/pictures/cache/"+random_str()+".png")
                await bot.send(event,Image(path=p))
            except:
                await bot.send(event,"出错，格式请按照/ba Blue#Archive")
    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("方舟十连" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain) == "方舟十连":
            logger.info("获取方舟抽卡结果")
            try:
                path = await arkGacha()
                logger.info("成功获取到抽卡结果")
                await bot.send(event, Image(path=path),True)
            except:
                logger.error("皱皮衮")
                await bot.send(event,"获取抽卡结果失败，请稍后再试")
    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("星铁十连" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain) == "星铁十连":
            logger.info("获取星铁抽卡结果")
            try:
                path = await starRailGacha()
                logger.info("成功获取到星铁抽卡结果")
                await bot.send(event, Image(path=path),True)
            except:
                logger.error("穹批衮")
                await bot.send(event,"获取抽卡结果失败，请稍后再试")
    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("ba十连" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain) == "ba十连":
            logger.info("获取ba抽卡结果")
            try:
                path = await bbbgacha(bbb)
                logger.info("成功获取到ba抽卡结果")
                await bot.send(event, Image(path=path),True)
            except:
                logger.error("碧批衮")
                await bot.send(event,"获取抽卡结果失败，请稍后再试")

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