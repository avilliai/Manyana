# -*- coding: utf-8 -*-
import datetime
import json
from asyncio import sleep

import httpx
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import MusicShare
from mirai import Startup, Shutdown

from plugins.historicalToday import steamEpic
from plugins.newsEveryDay import news, danxianglii
from plugins.picGet import picDwn
from plugins.translater import translate


def main(bot,proxy,nasa_api,app_id,app_key,logger):
    global data
    with open('data/scheduledTasks.yaml', 'r',encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    newsT=data.get("news").get("time").split("/")
    steamadd1 = data.get("steamadd1").get("time").split("/")
    astronomy=data.get("astronomy").get("time").split("/")
    moyu = data.get("moyu").get("time").split("/")
    constellation=data.get("constellation").get("time").split("/")
    if "danxiangli" in data:
        danxiangli=data.get("danxiangli").get("time").split("/")
    else:
        danxiangli="16/10".split("/")
        data["danxiangli"]={"text":"今日单向历"}
        data["danxiangli"]["time"]="16/10"
        data["danxiangli"]["groups"]=[699455559,12345]
        with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(data, file, allow_unicode=True)
    global scheduler
    scheduler = AsyncIOScheduler()


    @bot.on(Startup)
    def start_scheduler(_):
        scheduler.start()  # 启动定时器

    @bot.on(Shutdown)
    def stop_scheduler(_):
        scheduler.shutdown(True)  # 结束定时器

    @scheduler.scheduled_job(CronTrigger(hour=int(newsT[0]), minute=int(newsT[1])))
    async def newsEveryDay():
        logger.info("获取新闻")
        path = await news()
        logger.info("推送今日新闻")
        for i in data.get("news").get("groups"):
            try:
                await bot.send_group_message(int(i), [data.get("news").get("text"),Image(path=path)])
            except:
                logger.error("不存在的群"+str(i))

    @scheduler.scheduled_job(CronTrigger(hour=int(steamadd1[0]), minute=int(steamadd1[1])))
    async def steamEveryDay():
        logger.info("获取steam喜加一")
        path = await steamEpic()
        logger.info("推送今日喜加一列表")
        for i in data.get("steamadd1").get("groups"):
            try:
                if path==None or path=="":
                    return
                await bot.send_group_message(int(i), [data.get("steamadd1").get("text"), path])
            except:
                logger.error("不存在的群"+str(i))
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
            txta = await translate(response.json().get("explanation"), app_id=app_id, app_key=app_key, ori="en",
                                   aim="zh-CHS")
            txt = response.json().get("date") + "\n" + response.json().get("title") + "\n" + txta
            temp = {"path": "data/pictures/nasa/" + response.json().get("date") + ".png",
                    "oriTxt": response.json().get("explanation"), "transTxt": txt}

            data[datetime.datetime.now().strftime('%Y-%m-%d')] = temp

            with open('data/nasaTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(data, file, allow_unicode=True)
            for i in data.get("news").get("groups"):
                try:
                    await bot.send_group_message(int(i), [data.get("news").get("text"), Image(path=filename),txt])
                except:
                    logger.error("不存在的群" + str(i))
        except:
            logger.warning("获取每日天文图片失败")
    @scheduler.scheduled_job(CronTrigger(hour=int(moyu[0]), minute=int(moyu[1])))
    async def moyuEveryDay():
        logger.info("获取摸鱼人日历")
        path = await moyu()
        logger.info("推送摸鱼人日历")
        for i in data.get("moyu").get("groups"):
            try:
                await bot.send_group_message(int(i), [data.get("moyu").get("text"),Image(path=path)])
            except:
                logger.error("不存在的群"+str(i))
    @scheduler.scheduled_job(CronTrigger(hour=int(constellation[0]), minute=int(constellation[1])))
    async def constellationEveryDay():
        logger.info("获取星座运势")
        path = await moyu()
        logger.info("推送星座运势")
        for i in data.get("constellation").get("groups"):
            try:
                await bot.send_group_message(int(i), [data.get("constellation").get("text"),Image(path=path)])
            except:
                logger.error("不存在的群"+str(i))
    @bot.on(GroupMessage)
    async def addSubds(event: GroupMessage):
        global data
        if str(event.message_chain)=="/推送 摸鱼人日历":
            key="moyu"
        elif str(event.message_chain)=="/推送 每日天文":
            key="astronomy"
        elif str(event.message_chain)=="/推送 每日新闻":
            key="news"
        elif str(event.message_chain)=="/推送 喜加一":
            key="steamadd1"
        elif str(event.message_chain)=="/推送 每日星座":
            key="constellation"
        elif str(event.message_chain)=="/推送 单向历":
            key="danxiangli"
        else:
            return
        la=data.get(key).get("groups")
        if event.group.id not in la:
            la.append(event.group.id)
            data[key]["groups"]=la
            with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(data, file, allow_unicode=True)
            await bot.send(event,"添加订阅成功，推送时间："+str(data.get(key).get("time")))
        else:
            await bot.send(event,"添加失败，已经添加过对应的任务。")

    @scheduler.scheduled_job(CronTrigger(hour=int(danxiangli[0]), minute=int(danxiangli[1])))
    async def danxiangliy():
        logger.info("获取单向历")
        path = await danxianglii()
        logger.info("推送单向历")
        for i in data.get("danxiangli").get("groups"):
            try:
                if path == None:
                    return
                await bot.send_group_message(int(i), [data.get("danxiangli").get("text"),Image(path=path)])
            except:
                logger.error("不存在的群" + str(i))
    @bot.on(GroupMessage)
    async def cancelSubds(event: GroupMessage):
        global data
        if str(event.message_chain)=="/取消 摸鱼人日历":
            key="moyu"
        elif str(event.message_chain)=="/取消 每日天文":
            key="astronomy"
        elif str(event.message_chain)=="/取消 每日新闻":
            key="news"
        elif str(event.message_chain)=="/取消 喜加一":
            key="steamadd1"
        elif str(event.message_chain)=="/取消 每日星座":
            key="constellation"
        elif str(event.message_chain)=="/取消 单向历":
            key="danxiangli"
        else:
            return
        la=data.get(key).get("groups")
        la.remove(event.group.id)
        data[key]["groups"]=la
        with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(data, file, allow_unicode=True)
        await bot.send(event,"取消订阅成功")