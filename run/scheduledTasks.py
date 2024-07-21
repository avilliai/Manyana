# -*- coding: utf-8 -*-
import datetime
import sys
from asyncio import sleep

import httpx
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mirai import GroupMessage
from mirai import Image
from mirai import Startup, Shutdown

from plugins import weatherQuery
from plugins.aiReplyCore import modelReply
from plugins.extraParts import steamEpic
from plugins.newsEveryDay import news, danxianglii, moyu, xingzuo
from plugins.picGet import picDwn


def main(bot, proxy, nasa_api, logger):
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    api_KEY = result.get("weatherXinZhi")
    global data
    with open('data/scheduledTasks.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    keys = data.keys()
    newsT = data.get("news").get("time").split("/")
    steamadd1 = data.get("steamadd1").get("time").split("/")
    astronomy = data.get("astronomy").get("time").split("/")
    moyur = data.get("moyu").get("time").split("/")
    constellation = data.get("constellation").get("time").split("/")
    if "danxiangli" in data:
        danxiangli = data.get("danxiangli").get("time").split("/")
    else:
        danxiangli = "16/10".split("/")
        data["danxiangli"] = {"text": "今日单向历"}
        data["danxiangli"]["time"] = "16/10"
        data["danxiangli"]["groups"] = [699455559, 12345]
        with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(data, file, allow_unicode=True)
    global scheduler
    scheduler = AsyncIOScheduler()

    #早安推送信息必要内容
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    friendsAndGroups = result.get("加群和好友")
    aiReplyCore = result.get("chatGLM").get("aiReplyCore")
    trustDays = friendsAndGroups.get("trustDays")
    scheduledTasks = result.get("scheduledTasks")
    morningTime = str(scheduledTasks.get("morning").get("time")).split("/")
    morningText = scheduledTasks.get("morning").get("text")
    morningEnable = scheduledTasks.get("morning").get("enable")

    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        Userdata = yaml.load(file, Loader=yaml.FullLoader)
    global trustUser
    global userdict
    userdict = Userdata
    trustUser = []
    for i in userdict.keys():
        Userdata = userdict.get(i)
        try:
            times = int(str(Userdata.get('sts')))
            if times > trustDays:
                trustUser.append(str(i))

        except Exception as e:
            logger.error(f"用户{i}的sts数值出错，请打开data/userData.yaml检查，将其修改为正常数值")

    @bot.on(Startup)
    async def upDate(event: Startup):
        while True:
            await sleep(60)
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                Userdata = yaml.load(file, Loader=yaml.FullLoader)
            global trustUser
            global userdict
            userdict = Userdata
            trustUser = []
            for i in userdict.keys():
                Userdata = userdict.get(i)
                times = int(str(Userdata.get('sts')))
                if times > trustDays:
                    trustUser.append(str(i))

    @bot.on(Startup)
    def start_scheduler(_):
        scheduler.start()  # 启动定时器

    @bot.on(Shutdown)
    def stop_scheduler(_):
        try:
            scheduler.shutdown(True)  # 结束定时器
        except:
            pass
        try:
            sys.exit(1)
        except:
            pass

    @scheduler.scheduled_job(CronTrigger(hour=int(newsT[0]), minute=int(newsT[1])))
    async def newsEveryDay():
        logger.info("获取新闻")
        path = await news()
        logger.info("推送今日新闻")
        for i in data.get("news").get("groups"):
            try:
                await bot.send_group_message(int(i), [data.get("news").get("text"), Image(path=path)])
            except:
                logger.error("不存在的群" + str(i))

    @scheduler.scheduled_job(CronTrigger(hour=int(morningTime[0]), minute=int(morningTime[1])))
    async def MorningSendHello():
        global trustUser, userdict
        logger.info("早间天气推送")
        if morningEnable:
            for i in trustUser:
                try:
                    city = userdict.get(i).get("city")
                    logger.info(f"查询 {city} 天气")
                    wSult = await weatherQuery.querys(city, api_KEY)
                    # 发送天气消息
                    if aiReplyCore:
                        r = await modelReply(userdict.get(i).get("userName"), int(i),
                                             f"请你为我进行天气播报，下面是天气查询的结果：{wSult}")
                        await bot.send_friend_message(int(i), r)
                    else:
                        await bot.send_friend_message(int(i), morningText + wSult)
                except Exception as e:
                    logger.error(e)
                    continue

    @scheduler.scheduled_job(CronTrigger(hour=int(steamadd1[0]), minute=int(steamadd1[1])))
    async def steamEveryDay():
        logger.info("获取steam喜加一")
        path = await steamEpic()
        logger.info("推送今日喜加一列表")
        for i in data.get("steamadd1").get("groups"):
            try:
                if path is None or path == "":
                    return
                await bot.send_group_message(int(i), [data.get("steamadd1").get("text"), path])
            except:
                logger.error("不存在的群" + str(i))

    @scheduler.scheduled_job(CronTrigger(hour=int(astronomy[0]), minute=int(astronomy[1])))
    async def asffEveryDay():
        logger.info("获取今日nasa天文信息推送")
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
            txta = response.json().get("explanation")  #await translate(response.json().get("explanation"), "EN2ZH_CN")
            txt = response.json().get("date") + "\n" + response.json().get("title") + "\n" + txta
            temp = {"path": "data/pictures/nasa/" + response.json().get("date") + ".png",
                    "oriTxt": response.json().get("explanation"), "transTxt": txt}

            data[datetime.datetime.now().strftime('%Y-%m-%d')] = temp

            with open('data/nasaTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(data, file, allow_unicode=True)
            if aiReplyCore:
                r = await modelReply("用户", 000000, f"将下面这段内容翻译为中文:{txt}")
                txt = r
            for i in data.get("astronomy").get("groups"):
                try:
                    await bot.send_group_message(int(i), [data.get("astronomy").get("text"), Image(path=filename), txt])
                except:
                    logger.error("不存在的群" + str(i))
        except:
            logger.warning("获取每日天文图片失败")

    @scheduler.scheduled_job(CronTrigger(hour=int(moyur[0]), minute=int(moyur[1])))
    async def moyuEveryDay():
        logger.info("获取摸鱼人日历")
        path = await moyu()
        logger.info("推送摸鱼人日历")
        for i in data.get("moyu").get("groups"):
            try:
                await bot.send_group_message(int(i), [data.get("moyu").get("text"), Image(path=path)])
            except:
                logger.error("不存在的群" + str(i))

    @scheduler.scheduled_job(CronTrigger(hour=int(constellation[0]), minute=int(constellation[1])))
    async def constellationEveryDay():
        logger.info("获取星座运势")
        path = await xingzuo()
        logger.info("推送星座运势")
        for i in data.get("constellation").get("groups"):
            try:
                await bot.send_group_message(int(i), [data.get("constellation").get("text"), Image(path=path)])
            except:
                logger.error("不存在的群" + str(i))

    @bot.on(GroupMessage)
    async def addSubds(event: GroupMessage):
        global data
        try:
            head, cmd, *o = str(event.message_chain).strip().split()
        except ValueError:
            return
        if o or head != '/推送' or not cmd:
            return
        cmds = {"摸鱼人日历": "moyu", "每日天文": "astronomy", "每日新闻": "news", "喜加一": "steamadd1",
                "每日星座": "constellation", "单向历": "danxiangli", }
        key = cmds.get(cmd, 'unknown')
        if key == 'unknown':
            return
        if cmd == "所有订阅":
            for key in keys:
                la = data.get(key).get("groups")
                if event.group.id not in la:
                    la.append(event.group.id)
                    data[key]["groups"] = la
            with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(data, file, allow_unicode=True)
            await bot.send(event, "添加所有订阅成功")
        else:
            la = data.get(key).get("groups")
            if event.group.id not in la:
                la.append(event.group.id)
                data[key]["groups"] = la
                with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(data, file, allow_unicode=True)
                await bot.send(event, "添加订阅成功，推送时间：" + str(data.get(key).get("time")))
            else:
                await bot.send(event, "添加失败，已经添加过对应的任务。")

    @scheduler.scheduled_job(CronTrigger(hour=int(danxiangli[0]), minute=int(danxiangli[1])))
    async def danxiangliy():
        logger.info("获取单向历")
        path = await danxianglii()
        logger.info("推送单向历")
        for i in data.get("danxiangli").get("groups"):
            try:
                if path is None:
                    return
                await bot.send_group_message(int(i), [data.get("danxiangli").get("text"), Image(path=path)])
            except:
                logger.error("不存在的群" + str(i))

    @bot.on(GroupMessage)
    async def cancelSubds(event: GroupMessage):
        global data
        if str(event.message_chain) == "/取消 摸鱼人日历":
            key = "moyu"
        elif str(event.message_chain) == "/取消 每日天文":
            key = "astronomy"
        elif str(event.message_chain) == "/取消 每日新闻":
            key = "news"
        elif str(event.message_chain) == "/取消 喜加一":
            key = "steamadd1"
        elif str(event.message_chain) == "/取消 每日星座":
            key = "constellation"
        elif str(event.message_chain) == "/取消 单向历":
            key = "danxiangli"
        else:
            if str(event.message_chain) == "/取消 所有订阅":
                for key in keys:
                    la = data.get(key).get("groups")
                    if event.group.id in la:
                        la.remove(event.group.id)
                        data[key]["groups"] = la
                with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(data, file, allow_unicode=True)
                await bot.send(event, "取消所有订阅成功")
            return
        la = data.get(key).get("groups")
        if event.group.id in la:
            la.remove(event.group.id)
            data[key]["groups"] = la
            with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(data, file, allow_unicode=True)
            await bot.send(event, "取消订阅成功")
        else:
            await bot.send(event, "取消失败，没有添加过对应的任务。")
