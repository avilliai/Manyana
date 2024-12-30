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
from mirai.models import MusicShare
from mirai import Startup, Shutdown

from plugins import weatherQuery
from plugins.aiReplyCore import modelReply
from plugins.extraParts import steamEpic
from plugins.newsEveryDay import news, danxianglii, moyu, xingzuo,bingEveryDay
from plugins.toolkits import screenshot_to_pdf_and_png,picDwn


def main(bot,logger):
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    api_KEY = result.get("weatherXinZhi")
    proxy = result.get("proxy")
    proxies = {
            "http://": proxy,
            "https://": proxy
        }
    nasa_api=result.get("nasa_api")

    global scheduler
    scheduler = AsyncIOScheduler()

    global groupdata
    with open('data/scheduledTasks.yaml', 'r', encoding='utf-8') as file:
        groupdata = yaml.load(file, Loader=yaml.FullLoader)
    keys = groupdata.keys()

    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller = yaml.load(f.read(), Loader=yaml.FullLoader)
        scheduledTasks = controller.get("scheduledTasks")


    #早安推送信息必要内容
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    friendsAndGroups = result.get("加群和好友")
    aiReplyCore = result.get("chatGLM").get("aiReplyCore")
    trustDays = friendsAndGroups.get("trustDays")

    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        Userdata = yaml.load(file, Loader=yaml.FullLoader)
    global trustUser
    global userdict
    userdict = Userdata
    trustUser = []
    for i in userdict.keys():
        singleUserData = userdict.get(i)
        times = int(str(singleUserData.get('sts')))
        if times > trustDays:
            trustUser.append(str(i))

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
                singleUserData = userdict.get(i)
                times = int(str(singleUserData .get('sts')))
                if times > trustDays:
                    trustUser.append(str(i))

    @bot.on(Startup)
    def start_scheduler(_):
        create_dynamic_jobs()
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

    async def task_executor(task_name, task_info):
        logger.info(f"执行任务：{task_name}")
        global trustUser, userdict
        if task_name=="goodnight":
            morningText = task_info.get("text")
            friendList = await bot.friend_list()
            userli = [i.id for i in friendList.data]
            if task_info.get("onlyTrustUser"):
                userli2=[]
                for i in userdict:
                    try:
                        s=int(i)
                    except:
                        continue
                    singleUserData = userdict.get(i)
                    times = int(str(singleUserData.get('sts')))
                    if times > task_info.get("trustThreshold") and int(i) in userli:
                        userli2.append(str(i))
                userli = userli2
            for i in userli:
                try:
                    if aiReplyCore:
                        r = await modelReply(userdict.get(str(i)).get("userName"), int(i),
                                             f"请你对我进行晚安道别，直接发送结果即可，不要发送其他内容")
                        await bot.send_friend_message(int(i), r)
                    else:
                        await bot.send_friend_message(int(i), morningText)
                except Exception as e:
                    logger.error(e)
                    continue
                await sleep(6)
        elif task_name == "morning":
            morningText = task_info.get("text")
            friendList = await bot.friend_list()
            userli = [i.id for i in friendList.data]
            if task_info.get("onlyTrustUser"):
                userli2 = []
                for i in userdict:
                    try:
                        s=int(i)
                    except:
                        continue
                    singleUserData = userdict.get(i)
                    times = int(str(singleUserData.get('sts')))
                    if times > task_info.get("trustThreshold") and int(i) in userli:
                        userli2.append(str(i))
                userli = userli2
            for i in userli:
                try:
                    city = userdict.get(i).get("city")
                    logger.info(f"查询 {city} 天气")
                    if aiReplyCore:
                        wSult=await weatherQuery.fullQuery(city)
                        r = await modelReply(userdict.get(str(i)).get("userName"), int(i),
                                             f"请你为我进行天气播报，下面是天气查询的结果：{wSult}")
                        await bot.send_friend_message(int(i), r)
                    else:
                        wSult = await weatherQuery.querys(city, api_KEY)
                        await bot.send_friend_message(int(i), morningText + wSult)
                except Exception as e:
                    logger.error(e)
                    continue
                await sleep(6)
        elif task_name == "news":
            logger.info("获取新闻")
            path = await news()
            logger.info("推送今日新闻")
            for i in groupdata.get(task_name).get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text"), Image(path=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="steamadd1":
            logger.info("获取steam喜加一")
            path = await steamEpic()
            logger.info("推送今日喜加一列表")
            if path is None or path == "":
                return
            elif "错误" in path:
                logger.error(f"喜加一出错,{path}")
                return
            for i in groupdata.get("steamadd1").get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text"), path])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="astronomy":
            logger.info("获取今日nasa天文信息推送")
            # Replace the key with your own
            dataa = {"api_key": nasa_api}
            logger.info("发起nasa请求")
            try:
                # 拼接url和参数
                url = "https://api.nasa.gov/planetary/apod?" + "&".join([f"{k}={v}" for k, v in dataa.items()])
                async with httpx.AsyncClient(proxies=proxies) as client:
                    response = await client.get(url=url)
                logger.info("获取到结果" + str(response.json()))
                # logger.info("下载缩略图")
                filename = await picDwn(response.json().get("url"),
                                        "data/pictures/nasa/" + response.json().get("date") + ".png")
                txta = response.json().get(
                    "explanation")  # await translate(response.json().get("explanation"), "EN2ZH_CN")
                txt = response.json().get("date") + "\n" + response.json().get("title") + "\n" + txta
                if aiReplyCore:
                    r = await modelReply("用户", 000000, f"将下面这段内容翻译为中文:{txt}")
                    txt = r
                for i in groupdata.get("astronomy").get("groups"):
                    try:
                        await bot.send_group_message(int(i),
                                                     [task_info.get("text"), Image(path=filename), txt])
                    except:
                        logger.error("不存在的群" + str(i))
            except:
                logger.warning("获取每日天文图片失败")
        elif task_name=="moyu":
            logger.info("获取摸鱼人日历")
            path = await moyu()
            logger.info("推送摸鱼人日历")
            for i in groupdata.get("moyu").get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text"), Image(path=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="bingEveryDay":
            logger.info("获取bing图像")
            text,p=await bingEveryDay()
            logger.info("推送")
            for i in groupdata.get("bingEveryDay").get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text")+text, Image(path=p)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="constellation":
            logger.info("获取星座运势")
            path = await xingzuo()
            logger.info("推送星座运势")
            for i in groupdata.get("constellation").get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text"), Image(path=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="danxiangli":
            logger.info("获取单向历")
            path = await danxianglii()
            logger.info("推送单向历")
            for i in groupdata.get("danxiangli").get("groups"):
                try:
                    if path is None:
                        return
                    await bot.send_group_message(int(i), [task_info.get("text"), Image(path=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="bangumi":
            url = "https://www.bangumi.app/calendar/today"
            path = "data/pictures/cache/today-"
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            path = path + today + ".png"
            await screenshot_to_pdf_and_png(url, path, 1080, 3000)
            for i in groupdata.get("bangumi").get("groups"):
                try:
                    if path is None:
                        return
                    await bot.send_group_message(int(i), [task_info.get("text"), Image(path=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="nightASMR":
            logger.info("获取晚安ASMR")
            from plugins.youtube0 import ASMR_today,get_audio,get_img
            athor,title,video_id,length = await ASMR_today()
            imgurl = await get_img(video_id)
            audiourl = await get_audio(video_id)
            logger.info("推送晚安ASMR")
            st1 = "今日ASMR:"+title+"\n"
            st1 += "频道："+athor+"\n"
            st1 += f"时长：{length//60}分{length%60}秒\n"
            st2 = "======================\n"
            st2 += task_info.get("text")
            msg =  MusicShare(kind="QQMusic",
                              title=title,
                              summary=athor,
                              jump_url=f"https://www.amoyshare.com/player/?v={video_id}",
                              picture_url=imgurl,
                              music_url=audiourl,
                              brief='ASMR')
            for i in groupdata.get("nightASMR").get("groups"):
                try:
                    await bot.send_group_message(int(i), [st1,Image(url=imgurl),st2])
                    await bot.send_group_message(int(i),msg)
                except:
                    logger.error("不存在的群"+str(i))
        
    def create_dynamic_jobs():
        for task_name, task_info in scheduledTasks.items():
            if task_info.get('enable'):
                time_parts = task_info.get('time').split('/')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                scheduler.add_job(task_executor, CronTrigger(hour=hour, minute=minute), args=[task_name, task_info])

    @bot.on(GroupMessage)
    async def addSubds(event: GroupMessage):
        global groupdata
        try:
            head, cmd, *o = str(event.message_chain).strip().split()
        except ValueError:
            return
        if o or head != '/推送' or not cmd:
            return
        cmds = {"摸鱼人日历": "moyu",
                "每日天文": "astronomy",
                "每日新闻": "news",
                "喜加一": "steamadd1",
                "每日星座": "constellation",
                "单向历": "danxiangli",
                "bangumi日榜":"bangumi",
                "每日bing": "bingEveryDay",
                "所有订阅": "所有订阅",
                "晚安ASMR":"nightASMR"}
        key = cmds.get(cmd, 'unknown')
        if key == 'unknown':
            return
        if cmd == "所有订阅":
            for key in keys:
                la = groupdata.get(key).get("groups")
                if event.group.id not in la:
                    la.append(event.group.id)
                    groupdata[key]["groups"] = la
            with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(groupdata, file, allow_unicode=True)
            await bot.send(event, "添加所有订阅成功")
        else:
            la = groupdata.get(key).get("groups")
            if event.group.id not in la:
                la.append(event.group.id)
                groupdata[key]["groups"] = la
                with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(groupdata, file, allow_unicode=True)
                await bot.send(event, "添加订阅成功，推送时间：" + str(scheduledTasks.get(key).get("time")))
            else:
                await bot.send(event, "添加失败，已经添加过对应的任务。")

    @bot.on(GroupMessage)
    async def cancelSubds(event: GroupMessage):
        global groupdata
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
        elif str(event.message_chain)=="/取消 bangumi日榜":
            key="bangumi"
        elif str(event.message_chain)=="/取消 晚安ASMR":
            key="nightASMR"
        elif str(event.message_chain)=="/取消 每日bing":
            key="bingEveryDay"
        else:
            if str(event.message_chain) == "/取消 所有订阅":
                for key in keys:
                    la = groupdata.get(key).get("groups")
                    if event.group.id in la:
                        la.remove(event.group.id)
                        groupdata[key]["groups"] = la
                with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(groupdata, file, allow_unicode=True)
                await bot.send(event, "取消所有订阅成功")
            return
        la = groupdata.get(key).get("groups")
        if event.group.id in la:
            la.remove(event.group.id)
            groupdata[key]["groups"] = la
            with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(groupdata, file, allow_unicode=True)
            await bot.send(event, "取消订阅成功")
        else:
            await bot.send(event, "取消失败，没有添加过对应的任务。")
