# -*- coding: utf-8 -*-
import json
import os
import datetime
import random
import time
import sys
from asyncio import sleep

import requests
from fuzzywuzzy import fuzz,process
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from mirai import Image, Voice, AtAll
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai import Startup, Shutdown
from mirai.models import BotJoinGroupEvent, MemberCardChangeEvent
from mirai.models.events import NudgeEvent
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from MoeGoe import voiceGenerate
from plugins.RandomStr.RandomStr import random_str
#from plugins.gitZen import get_zen
from plugins.moyu import moyu
from plugins.newsEveryday import news
from plugins.weatherQ import weatherQ
from readConfig import readConfig
from trans import translate


def main(bot,master):
    time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(time1 + '| scheduler module loaded successfully 已加载--- 定时任务 ---模块')

    file = open('Config\\zen.txt', 'r')
    js = file.read()
    global zen
    zen = json.loads(js)

    file = open('Config/moyu/groups.txt', 'r')
    js = file.read()
    global groupSend
    groupSend=0
    global severGroups
    global severGroupsa
    severGroupsa = json.loads(js)
    severGroups = severGroupsa.keys()

    time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(time1 + '| 定时任务服务群聊读取完毕')

    file = open('Config\\signDict.txt', 'r')
    js = file.read()
    global trustUser
    global userdict
    userdict = json.loads(js)
    trustUser = []
    for i in userdict.keys():
        data = userdict.get(i)
        times = int(str(data.get('sts')))
        if times > 3:
            trustUser.append(str(i))

    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(time + '| 已读取定时早安推送对象' + str(len(trustUser)) + '个')
    global live_status
    live_status=0



    # 这里是定时任务区
    # 定时摸鱼,可以在Config//moyu//中添加群
    global scheduler
    scheduler = AsyncIOScheduler()

    @bot.on(Startup)
    def start_scheduler(_):
        scheduler.start()  # 启动定时器
        print('当前路径' + sys.argv[0])
        Path = sys.argv[0][:-20]



    @bot.on(Shutdown)
    def stop_scheduler(_):
        scheduler.shutdown(True)  # 结束定时器
    '''@bot.on(Startup)
    async def sensor(event:Startup):
        global live_status
        while True:
            await sleep(60)
            url = "https://api.live.bilibili.com/room/v1/Room/room_init?id=27916071"

            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54",
                "Referer": "https://weibo.com/"}
            r = requests.get(url, headers=headers).content
            asf = json.loads(r.decode('UTF-8'))
            if asf.get("data").get("live_status")!=live_status:
                if asf.get("data").get("live_status")==0:
                    if str(event.group.permission) != str('Permission.Member'):
                        await bot.send_group_message(704469415, (AtAll(),"主播下播了，明天见ヾ(≧▽≦*)o"))
                    else:
                        await bot.send_group_message(704469415,  "主播下播了，明天见ヾ(≧▽≦*)o")
                if asf.get("data").get("live_status")==1:
                    if str(event.group.permission) != str('Permission.Member'):
                        await bot.send_group_message(704469415, (AtAll(),"主播正在直播φ(゜▽゜*)♪"))
                    else:
                        await bot.send_group_message(704469415, "主播正在直播φ(゜▽゜*)♪")
                live_status=asf.get("data").get("live_status")

            else:
                print("检测直播状态")'''


    @bot.on(Startup)
    async def updateData(event: Startup):
        while True:
            await sleep(360)
            file = open('Config\\signDict.txt', 'r')
            js = file.read()
            file.close()
            global trustUser
            global userdict
            userdict = json.loads(js)
            trustUser = []
            for i in userdict.keys():
                data = userdict.get(i)
                times = int(str(data.get('sts')))
                if times > 3:
                    trustUser.append(str(i))

            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(time + '| 已更新定时早安推送对象,当前共有' + str(len(trustUser)) + '个')

            file = open('Config/moyu/groups.txt', 'r')
            js = file.read()
            global groupSend
            groupSend = 0
            global severGroups
            global severGroupsa
            severGroupsa = json.loads(js)
            severGroups = severGroupsa.keys()

            time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(time1 + '| 定时任务服务群聊更新完毕')


    # 向信任用户报早安
    '''@scheduler.scheduled_job(CronTrigger(hour=7, minute=17))
    async def timer():

        for i in trustUser:
            data = userdict.get(str(i))
            city = data.get('city')
            weather = weatherQ(city)
            intTrans = int(i)
            await sleep(5)
            try:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 正在向好友' + str(i) + '发送早安')
                a=random.choice(['（⊙ｏ⊙）','(＃°Д°)','（*゜ー゜*）','(。_。)','...(*￣０￣)ノ','o((⊙﹏⊙))o','..(((m -__-)m','…(⊙_⊙;)','¯\(°_o)/¯','(￣┰￣*)','(→_→)o(><；)','ooΣ(っ °Д °;)っ','∑( 口 ||','┌(。Д。)┐','(°ー°〃)','ε=ε=ε=(~￣▽￣)~','(ノω<。)ノ))☆.。)'])
                try:
                    await bot.send_friend_message(intTrans, '早上好，这是今天的天气\n'+a+'\n'+weather)
                except:
                    await bot.send_temp_message(intTrans, '早上好，这是今天的天气\n' + a + '\n' + weather)
            except:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 指定好友' + str(intTrans) + '不存在或已删除')'''

    # 向信任用户报早安
    @scheduler.scheduled_job(CronTrigger(hour=7, minute=17))
    async def timer():

        for i in trustUser:
            data = userdict.get(str(i))
            city = data.get('city')
            weather = weatherQ(city)
            intTrans = int(i)
            await sleep(5)
            try:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 正在向好友' + str(i) + '发送早安')
                a = random.choice(
                    ['（⊙ｏ⊙）', '(＃°Д°)', '（*゜ー゜*）', '(。_。)', '...(*￣０￣)ノ', 'o((⊙﹏⊙))o', '..(((m -__-)m', '…(⊙_⊙;)',
                     '¯\(°_o)/¯', '(￣┰￣*)', '(→_→)o(><；)', 'ooΣ(っ °Д °;)っ', '∑( 口 ||', '┌(。Д。)┐', '(°ー°〃)',
                     'ε=ε=ε=(~￣▽￣)~', '(ノω<。)ノ))☆.。)'])
                try:
                    await bot.send_friend_message(intTrans, '早上好，这是今天的天气\n' + a + '\n' + weather)
                    if '雨' in weather:
                        await bot.send_friend_message(intTrans,"似乎有雨呢.....要记得带伞哦")
                except:
                    await bot.send_temp_message(intTrans, '早上好，这是今天的天气\n' + a + '\n' + weather)
            except:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 指定好友' + str(intTrans) + '不存在或已删除')

    # 摸鱼人日历
    @scheduler.scheduled_job(CronTrigger(hour=16, minute=55))
    async def timer():
        moyuPic = moyu()
        for i in severGroups:
            intTrans = int(i)
            await sleep(5)
            try:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 正在向群' + str(i) + '发送摸鱼人日历')
                await bot.send_group_message(intTrans, Image(path=moyuPic))
            except:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 指定群' + str(intTrans) + '不存在或已退出')






    @bot.on(GroupMessage)
    async def GroupSend(event: GroupMessage):
        if str(event.message_chain)=='notice' and str(event.sender.id)==str(master):
            global groupSend
            await bot.send(event,'请编辑更新通知内容：')
            groupSend = 1

    @bot.on(GroupMessage)
    async def sendPart(event: GroupMessage):
        global groupSend
        if str(event.sender.id)==str(master) and groupSend ==1:
            await bot.send(event, '正在向已加入的群发送更新公告.....')
            for i in severGroups:
                intTrans = int(i)
                await sleep(4)

                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 正在向群'+str(i)+'群发:\n'+str(event.message_chain))
                groupSend = 0

                try:
                    await bot.send_group_message(intTrans, event.message_chain)
                except:
                    time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(time1 + '| 指定群' + str(intTrans) + '不存在或已退出')


    @scheduler.scheduled_job(CronTrigger(hour=17, minute=50))
    async def timer():
        global severGroups
        ranpath = random_str()
        out = 'plugins\\voices\\' + ranpath + '.wav'

        tex = '[JA]' + translate('加油......今天也很棒了') + '[JA]'
        voiceGenerate(tex, out)
        for i in severGroups:
            intTrans = int(i)
            await sleep(3)
            time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(time1 + '| 正在向群' + str(i) + '发送下班提示' )


            try:
                await bot.send_group_message(intTrans, Voice(path=out))
            except:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 指定群'+str(intTrans)+'不存在或已退出')

    # 早八新闻自动推送
    @scheduler.scheduled_job(CronTrigger(hour=7, minute=40))
    async def timer():
        newsPic = news()
        global severGroups
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ranpath = random_str()
        out = 'plugins\\voices\\' + ranpath + '.wav'
        tex = '[JA]' + translate('早上好........已经为您整理好了今天的新闻！.......有什么有趣的事情吗?') + '[JA]'
        voiceGenerate(tex, out)
        print(time + '| 新闻事件-----> ')
        for i in severGroups:
            time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(time1 + '| 正在向群' + str(i) + '推送新闻')
            intTrans = int(i)

            try:
                await bot.send_group_message(intTrans, Image(path=newsPic))
                await sleep(2)
                await bot.send_group_message(intTrans, Voice(path=out))
            except:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 指定群' + str(intTrans) + '不存在或已退出')

    # 中午推送github禅语
    @scheduler.scheduled_job(CronTrigger(hour=12, minute=38))
    async def timer():
        global zen
        global severGroups
        time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(time1 + '| 禅语-----> ')
        ranpath = random_str()
        out = 'plugins\\voices\\' + ranpath + '.wav'
        tex = '[JA]' + translate('这是今天的禅语哦，希望你喜欢!') + '[JA]'
        voiceGenerate(tex, out)
        for i in severGroups:
            time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(time1 + '| 正在向群' + str(i) + '推送禅语')
            intTrans = int(i)

            zen1 = zen.get(random.choice(zen.keys()))
            try:
                await bot.send_group_message(intTrans, zen1)
                await bot.send_group_message(intTrans, Voice(path=out))
            except:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 指定群' + str(intTrans) + '不存在或已退出')

    # 早八问候
    @scheduler.scheduled_job(CronTrigger(hour=8, minute=1))
    async def timer():
        global severGroups
        ranpath = random_str()
        out = 'plugins\\voices\\' + ranpath + '.wav'
        tex = '[JA]' + translate('早上好......记得吃早饭~......没有特别关心你哦~！') + '[JA]'
        voiceGenerate(tex, out)
        for i in severGroups:
            intTrans = int(i)
            time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(time1 + '| 执行早八问候-----> '+str(intTrans))


            try:
                await bot.send_group_message(intTrans, Voice(path=out))
            except:
                time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(time1 + '| 指定群' + str(intTrans) + '不存在或已退出')
    # 追加推送群聊
    @bot.on(GroupMessage)
    async def addGroup(event: GroupMessage):
        if str(event.message_chain).startswith('添加群#'):
            global severGroupsa
            global severGroups
            s = str(event.message_chain).split('#')
            severGroupsa[str(s[1])]=str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            severGroups=severGroupsa.keys()
            newData = json.dumps(severGroupsa)
            with open('Config/moyu/groups.txt', 'w') as fp:
                fp.write(newData)

    @bot.on(GroupMessage)
    async def autoAdd(event: GroupMessage):
        global severGroupsa
        global severGroups
        if str(event.group.id) not in severGroupsa.keys():

            severGroupsa[str(event.group.id)]=str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            severGroups=severGroupsa.keys()
            newData = json.dumps(severGroupsa)
            time1=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(time1 + '| 新增群：'+str(event.group.id))
            with open('Config/moyu/groups.txt', 'w') as fp:
                fp.write(newData)