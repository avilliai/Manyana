# -*- coding: utf-8 -*-
import datetime
import json
import re
import time
from asyncio import sleep

import httpx
import requests
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mirai import Image, Voice, AtAll
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import MusicShare, App, Xml, Json
from mirai import Startup, Shutdown

from plugins.RandomStr import random_str


def main(bot,master,botName,logger):
    global live
    with open('data/biliMonitor.yaml', 'r', encoding='utf-8') as file:
        live = yaml.load(file, Loader=yaml.FullLoader)
    print("live")
    global temp
    temp={}
    global lists
    lists={}
    for i in live:
        lists[i]=0
    print(lists)


    @bot.on(Startup)
    async def monitor(event:GroupMessage):
        while True:

            for i in lists:
                try:
                    url = "https://api.live.bilibili.com/room/v1/Room/room_init?id="+str(i)

                    headers = {
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54",
                        "Referer": "https://weibo.com/"}
                    r = requests.get(url, headers=headers).content
                    asf = json.loads(r.decode('UTF-8'))
                    #print(asf)
                    if asf.get("data").get("live_status") != lists.get(i):
                        if asf.get("data").get("live_status") == 0:

                            for ia in live.get(i).get("group"):
                                try:
                                    #await bot.send_group_message(int(ia), AtAll())
                                    await bot.send_group_message(int(ia), "主播下播了，明天见ヾ(≧▽≦*)o")
                                except:
                                    await bot.send_group_message(int(ia), "主播下播了，明天见ヾ(≧▽≦*)o")
                        if asf.get("data").get("live_status") == 1:
                            for ia in live.get(i).get("group"):
                                try:
                                    #await bot.send_group_message(int(ia), AtAll() )
                                    await bot.send_group_message(int(ia),"主播正在直播φ(゜▽゜*)♪")
                                    logger.info("检测到直播进行中")

                                    await bot.send_group_message(int(ia), App(content=live.get(i).get("app")))
                                except:
                                    await bot.send_group_message(int(ia), "主播正在直播φ(゜▽゜*)♪")
                                    logger.info("检测到直播进行中")

                                    await bot.send_group_message(int(ia), App(content=live.get(i).get("app")))

                        lists[i] = asf.get("data").get("live_status")
                except:
                    logger.warning("直播订阅异常，请忽略")
                    continue
            await sleep(80)

    @bot.on(GroupMessage)
    async def bilimON1(event: GroupMessage):
        global live
        if str(event.message_chain).startswith("取消直播订阅#"):
            id1=str(event.message_chain).split("#")[1]
            logger.info("尝试取消订阅"+id1)
            id1=int(id1)
            try:
                d1=live.get(id1).get("group")
                logger.info("取到数值")
                logger.info(str(d1))
                d1.pop(id1)
                logger.info("弹出")
                t1=[]

                if d1==t1:
                    live.pop(id1)
                else:
                    live[id1]["group"]=d1
                with open('data/biliMonitor.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(live, file, allow_unicode=True)
                logger.warning("取消了直播订阅")
                await bot.send(event, "取消了对"+str(id1)+"的直播订阅")
            except:
                await bot.send(event,"error，请检查直播房间号是否正确")

    @bot.on(GroupMessage)
    async def bilimON1(event: GroupMessage):
        if str(event.message_chain)=="添加直播":
            await bot.send(event,"请从bilibili分享直播到群内，bot将记录数据并添加任务")
            temp[event.group.id]={"step":1}
    @bot.on(GroupMessage)
    async def bilimON(event:GroupMessage):
        global live
        global lists
        try:
            if event.message_chain.count(App) and temp.get(event.group.id).get("step")==1:
                con = event.message_chain.get(App)[0].content

                content = int(re.findall(r"(?<=房间号：).*?(?=\")", con)[0])
                #print(content) # ['27916071']
                logger.info("增加直播订阅"+str(content))
                if content in live:
                    groups=live.get(content).get("group")
                    if event.group.id in groups:
                        await bot.send(event,"已添加过订阅")
                    else:
                        groups.append(event.group.id)
                        live[content]["group"]=groups
                else:
                    live[content]={"app":con,"group":[event.group.id]}
                await bot.send(event,"成功添加了对"+str(content)+"的直播订阅")
                temp.pop(event.group.id)
                logger.info(live)
                with open('data/biliMonitor.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(live, file, allow_unicode=True)
                lists[content]=0
                #await bot.send(event,"已添加订阅")
                #print(event.message_chain.get(App)[0].content,type(event.message_chain.get(App)[0].content))
                #dat1=event.message_chain.get(App)[0].content

                #await bot.send(event,App(content=str(dat1)))
        except:
            pass
